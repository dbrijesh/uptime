import os
import json
import time
from datetime import datetime
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = "/home/actions-runner/_diag"
LOG_GROUP = "/var/log"
REGION = "ap-south-1"

client = boto3.client("logs", region_name=REGION)

# Keep track of already processed files to avoid re-uploading
processed_files = set()


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def ensure_log_stream(run_id):
    try:
        client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=str(run_id))
        log(f"Created log stream: {run_id}")
    except client.exceptions.ResourceAlreadyExistsException:
        log(f"Log stream already exists: {run_id}")


def extract_run_id(file_path):
    buffer = ""
    run_id = None
    with open(file_path, "r") as f:
        for line in f:
            buffer += line
            buffer_strip = buffer.strip()
            if buffer_strip.startswith("{") and buffer_strip.endswith("}"):
                try:
                    data = json.loads(buffer_strip)
                    if "contextData" in data and "github.d" in data["contextData"]:
                        for obj in data["contextData"]["github.d"]:
                            if obj.get("k") == "run_id":
                                run_id = obj.get("v")
                                log(f"Found run_id: {run_id} in {file_path}")
                                return run_id
                except json.JSONDecodeError:
                    continue
                finally:
                    buffer = ""
    log(f"No run_id found in {file_path}")
    return run_id


def upload_file_to_cloudwatch(file_path, run_id):
    ensure_log_stream(run_id)
    with open(file_path, "r") as f:
        lines = f.readlines()

    if not lines:
        log(f"File {file_path} is empty, skipping upload.")
        return

    ts = int(time.time() * 1000)
    log_events = [{"timestamp": ts, "message": line.strip()} for line in lines if line.strip()]

    BATCH_SIZE = 10000
    sequence_token = None

    for i in range(0, len(log_events), BATCH_SIZE):
        batch = log_events[i:i + BATCH_SIZE]
        kwargs = {
            "logGroupName": LOG_GROUP,
            "logStreamName": str(run_id),
            "logEvents": batch
        }
        if sequence_token:
            kwargs["sequenceToken"] = sequence_token
        resp = client.put_log_events(**kwargs)
        sequence_token = resp.get("nextSequenceToken")

    log(f"Uploaded {len(log_events)} lines from {file_path} -> stream {run_id}")
    processed_files.add(file_path)


def is_file_today(file_path):
    """Check if file was created/modified today"""
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    today = datetime.today()
    return file_mtime.date() == today.date()


class WorkerLogHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_name = os.path.basename(event.src_path)
        if "Worker_" in file_name and event.src_path not in processed_files and is_file_today(event.src_path):
            log(f"New Worker log detected: {event.src_path}")
            time.sleep(2)  # wait for file to stabilize
            run_id = extract_run_id(event.src_path)
            if run_id:
                upload_file_to_cloudwatch(event.src_path, run_id)
            else:
                log(f"⚠️ Skipping upload, no run_id found in {event.src_path}")
                processed_files.add(event.src_path)


def process_existing_files():
    """Process files already present in LOG_DIR"""
    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)
        if file_path in processed_files:
            continue
        if "Worker_" in file_name and is_file_today(file_path):
            log(f"Processing existing Worker log: {file_path}")
            run_id = extract_run_id(file_path)
            if run_id:
                upload_file_to_cloudwatch(file_path, run_id)
            else:
                log(f"⚠️ Skipping upload, no run_id found in {file_path}")
                processed_files.add(file_path)


def main():
    log(f"Starting Worker log uploader, watching directory: {LOG_DIR}")
    process_existing_files()

    event_handler = WorkerLogHandler()
    observer = Observer()
    observer.schedule(event_handler, LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log("Stopping Worker log uploader...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

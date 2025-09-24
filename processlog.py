import os
import json
import time
from datetime import datetime
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = "/actions-runner/_diag"
LOG_GROUP = "/var/log"
REGION = "us-east-2"

client = boto3.client("logs", region_name=REGION)

# Keep track of already processed files
processed_files = set()


def log(msg):
    """Helper to print timestamped messages"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def ensure_log_stream(run_id):
    """Ensure log stream exists for this run_id"""
    try:
        client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=str(run_id))
        log(f"Created log stream: {run_id}")
    except client.exceptions.ResourceAlreadyExistsException:
        log(f"Log stream already exists: {run_id}")


def extract_run_id(file_path):
    """
    Extract run_id from JSON entries in the log file.
    Supports multi-line JSON with structure:
    {"contextData":{"github":{"t":2,"d":[{"k":"run_id","v":"123456"}]}}}
    """
    buffer = ""
    with open(file_path, "r") as f:
        for line in f:
            buffer += line
            buffer_strip = buffer.strip()
            if buffer_strip.startswith("{") and buffer_strip.endswith("}"):
                try:
                    data = json.loads(buffer_strip)
                    github_data = data.get("contextData", {}).get("github", {}).get("d", [])
                    for obj in github_data:
                        if obj.get("k") == "run_id":
                            run_id = obj.get("v")
                            log(f"Found run_id: {run_id} in {file_path}")
                            return run_id
                except json.JSONDecodeError:
                    continue
                finally:
                    buffer = ""
    return None


def wait_for_job_completed(file_path, timeout=300, interval=5):
    """
    Wait until 'Job completed.' appears in the file, or timeout (seconds) reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        with open(file_path, "r") as f:
            content = f.read()
            if "Job completed." in content:
                log(f"'Job completed.' found in {file_path}")
                return True
        time.sleep(interval)
    log(f"⚠️ Timeout waiting for 'Job completed.' in {file_path}")
    return False


def upload_file_to_cloudwatch(file_path, run_id):
    """Upload entire log file contents to CloudWatch Logs"""
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
            time.sleep(2)  # wait briefly for file to stabilize

            if wait_for_job_completed(event.src_path):
                run_id = extract_run_id(event.src_path)
                if run_id:
                    upload_file_to_cloudwatch(event.src_path, run_id)
                else:
                    log(f"⚠️ run_id not found in {event.src_path}, skipping upload")
                    processed_files.add(event.src_path)
            else:
                log(f"⚠️ Skipping {event.src_path} as 'Job completed.' not found")
                processed_files.add(event.src_path)


def process_existing_files():
    """Process files already present in LOG_DIR"""
    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)
        if file_path in processed_files:
            continue
        if "Worker_" in file_name and is_file_today(file_path):
            log(f"Processing existing Worker log: {file_path}")
            if wait_for_job_completed(file_path):
                run_id = extract_run_id(file_path)
                if run_id:
                    upload_file_to_cloudwatch(file_path, run_id)
                else:
                    log(f"⚠️ run_id not found in {file_path}, skipping upload")
                    processed_files.add(file_path)
            else:
                log(f"⚠️ Skipping {file_path} as 'Job completed.' not found")
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


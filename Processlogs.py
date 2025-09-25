import os
import time
import re
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = "/actions-runner/_diag"
LOG_GROUP = "/var/log"
REGION = "us-east-2"

client = boto3.client("logs", region_name=REGION)

# Keep track of already processed files
processed_files = set()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def log(msg, level="info"):
    """Helper for consistent log formatting"""
    if level == "error":
        logging.error(msg)
    elif level == "warn":
        logging.warning(msg)
    else:
        logging.info(msg)


def ensure_log_stream(run_id):
    """Ensure log stream exists for this run_id"""
    try:
        client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=str(run_id))
        log(f"Created log stream: {run_id}")
    except client.exceptions.ResourceAlreadyExistsException:
        log(f"Log stream already exists: {run_id}")


def extract_run_id(file_path):
    """Extract run_id from log content using regex"""
    pattern = re.compile(r'"k"\s*:\s*"run_id"\s*,\s*"v"\s*:\s*"(\d+)"', re.MULTILINE)
    try:
        with open(file_path, "r") as f:
            content = f.read()
        match = pattern.search(content)
        if match:
            run_id = match.group(1)
            log(f"Found run_id: {run_id} in {file_path}")
            return run_id
        else:
            log(f"⚠️ run_id not found in {file_path}", "warn")
            return "unknown-run-id"
    except Exception as e:
        log(f"❌ Error reading {file_path} for run_id: {e}", "error")
        return "unknown-run-id"


def wait_for_job_completed(file_path, timeout=300, interval=5):
    """Wait until 'Job completed.' appears in the file, or timeout reached"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if "Job completed." in content:
                    log(f"'Job completed.' found in {file_path}")
                    return True
        except Exception as e:
            log(f"❌ Error reading {file_path}: {e}", "error")
        time.sleep(interval)
    log(f"⚠️ Timeout waiting for 'Job completed.' in {file_path}", "warn")
    return False


def upload_file_to_cloudwatch(file_path, run_id):
    """Upload entire log file contents to CloudWatch Logs"""
    ensure_log_stream(run_id)

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        log(f"❌ Failed to read {file_path}: {e}", "error")
        return

    if not lines:
        log(f"⚠️ File {file_path} is empty, skipping upload", "warn")
        return

    ts = int(time.time() * 1000)
    log_events = [{"timestamp": ts, "message": line.strip()} for line in lines if line.strip()]

    BATCH_SIZE = 10000
    sequence_token = None

    try:
        for i in range(0, len(log_events), BATCH_SIZE):
            batch = log_events[i:i + BATCH_SIZE]
            kwargs = {
                "logGroupName": LOG_GROUP,
                "logStreamName": str(run_id),
                "logEvents": batch,
            }
            if sequence_token:
                kwargs["sequenceToken"] = sequence_token
            resp = client.put_log_events(**kwargs)
            sequence_token = resp.get("nextSequenceToken")

        log(f"✅ Uploaded {len(log_events)} lines from {file_path} -> stream {run_id}")
        processed_files.add(file_path)
    except ClientError as e:
        log(f"❌ Failed to upload {file_path} to CloudWatch: {e}", "error")
        # Here you can add SNS or email notification
        # Example: boto3.client("sns").publish(TopicArn="...", Message=str(e), Subject="Log upload failed")


class WorkerLogHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_name = os.path.basename(event.src_path)
        if "Worker_" in file_name and event.src_path not in processed_files:
            log(f"📂 New Worker log detected: {event.src_path}")
            time.sleep(2)  # wait briefly for file to stabilize

            if wait_for_job_completed(event.src_path):
                run_id = extract_run_id(event.src_path)
                upload_file_to_cloudwatch(event.src_path, run_id)
            else:
                log(f"⚠️ Skipping {event.src_path} as 'Job completed.' not found", "warn")
                processed_files.add(event.src_path)


def process_existing_files():
    """Process files already present in LOG_DIR"""
    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)
        if file_path in processed_files:
            continue
        if "Worker_" in file_name:
            log(f"🔄 Processing existing Worker log: {file_path}")
            if wait_for_job_completed(file_path):
                run_id = extract_run_id(file_path)
                upload_file_to_cloudwatch(file_path, run_id)
            else:
                log(f"⚠️ Skipping {file_path} as 'Job completed.' not found", "warn")
                processed_files.add(file_path)


def main():
    log(f"🚀 Starting Worker log uploader, watching directory: {LOG_DIR}")
    process_existing_files()

    event_handler = WorkerLogHandler()
    observer = Observer()
    observer.schedule(event_handler, LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log("🛑 Stopping Worker log uploader...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

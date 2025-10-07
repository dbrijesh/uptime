#!/bin/bash
set -euo pipefail

# ===== Configuration =====
RUN_ID=${GITHUB_RUN_ID:-"manual-$(date +%s)"}
JOB_NAME=${GITHUB_JOB:-"unknown"}
REPO_NAME=${GITHUB_REPOSITORY:-"unknown-repo"}
RUNNER_NAME=${RUNNER_NAME:-$(hostname)}
LOG_GROUP="${LOG_GROUP_NAME:-githubrunnerlogs}"
BLOCKS_DIR="/actions-runner/_diag/blocks"
REGION="${AWS_REGION:-us-east-2}"
MAX_BATCH_SIZE=10
MAX_EVENT_SIZE=262144
TIME_WINDOW=${LOG_TIME_WINDOW:-10}

# Tracking file to prevent duplicate processing
TRACKING_FILE="/actions-runner/_diag/.processed_blocks"
# Whether to delete files after successful upload
PURGE_AFTER_UPLOAD=${PURGE_LOGS:-false}

echo "🪵 [POST-JOB] Streaming runner logs to CloudWatch"
echo "   Runner: $RUNNER_NAME"
echo "   Run ID: $RUN_ID"
echo "   Job: $JOB_NAME"
echo "   Repository: $REPO_NAME"
echo "   Time window: Last $TIME_WINDOW minutes"
echo "   Purge after upload: $PURGE_AFTER_UPLOAD"

# ===== Dependency Check =====
if ! command -v aws &> /dev/null; then
  echo "⚠️ Warning: aws cli not found, skipping log upload"
  exit 0
fi

if ! command -v jq &> /dev/null; then
  echo "⚠️ Warning: jq not found, skipping log upload"
  exit 0
fi

# ===== Verify AWS credentials =====
if ! aws sts get-caller-identity --region "$REGION" &> /dev/null; then
  echo "⚠️ Warning: AWS credentials not configured, skipping log upload"
  exit 0
fi

# ===== Check blocks directory =====
if [ ! -d "$BLOCKS_DIR" ]; then
  echo "ℹ️ No blocks directory found at $BLOCKS_DIR, nothing to upload"
  exit 0
fi

# ===== Initialize tracking file =====
touch "$TRACKING_FILE" 2>/dev/null || true

# ===== Clean up old entries from tracking file (older than 2 hours) =====
if [ -f "$TRACKING_FILE" ]; then
  CUTOFF_TIME=$(($(date +%s) - 7200))  # 2 hours ago
  while IFS='|' read -r filepath timestamp; do
    if [ -n "$timestamp" ] && [ "$timestamp" -gt "$CUTOFF_TIME" ]; then
      echo "${filepath}|${timestamp}" >> "${TRACKING_FILE}.tmp"
    fi
  done < "$TRACKING_FILE"
  
  if [ -f "${TRACKING_FILE}.tmp" ]; then
    mv "${TRACKING_FILE}.tmp" "$TRACKING_FILE"
  else
    > "$TRACKING_FILE"  # Empty the file if no recent entries
  fi
fi

# ===== Find recently modified files =====
RECENT_BLOCKS=$(find "$BLOCKS_DIR" -type f -mmin -${TIME_WINDOW} 2>/dev/null | sort || true)

if [ -z "$RECENT_BLOCKS" ]; then
  echo "ℹ️ No files modified in the last $TIME_WINDOW minutes"
  exit 0
fi

TOTAL_EVENTS=0
TOTAL_FILES=0
SKIPPED_FILES=0
PURGED_FILES=0

# ===== Create log stream name =====
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STREAM_NAME="${RUNNER_NAME}/${REPO_NAME//\//-}/${RUN_ID}/${JOB_NAME}/${TIMESTAMP}"

echo "📤 Creating log stream: $STREAM_NAME"

# ===== Create log stream =====
aws logs create-log-stream \
  --region "$REGION" \
  --log-group-name "$LOG_GROUP" \
  --log-stream-name "$STREAM_NAME" 2>/dev/null || true

# ===== Get sequence token =====
SEQUENCE_TOKEN=$(aws logs describe-log-streams \
  --region "$REGION" \
  --log-group-name "$LOG_GROUP" \
  --log-stream-name-prefix "$STREAM_NAME" \
  --max-items 1 \
  --query "logStreams[?logStreamName=='$STREAM_NAME'].uploadSequenceToken" \
  --output text 2>/dev/null || echo "")

# ===== Process block files =====
for blockfile in $RECENT_BLOCKS; do
  [ -f "$blockfile" ] || continue
  
  BLOCK_NAME=$(basename "$blockfile")
  FILE_MTIME=$(stat -c %Y "$blockfile" 2>/dev/null || date +%s)
  
  # ===== Check if this file was already processed =====
  FILE_IDENTIFIER="${blockfile}|${FILE_MTIME}"
  if grep -q "^${blockfile}|${FILE_MTIME}$" "$TRACKING_FILE" 2>/dev/null; then
    echo "   ⏭️  Skipping: $BLOCK_NAME (already processed)"
    SKIPPED_FILES=$((SKIPPED_FILES + 1))
    continue
  fi
  
  echo "   📄 Processing: $BLOCK_NAME"
  
  TOTAL_FILES=$((TOTAL_FILES + 1))
  EVENT_BATCH="["
  BATCH_COUNT=0
  
  # Get file modification time for base timestamp
  BASE_TIMESTAMP=$((FILE_MTIME * 1000))  # Convert to milliseconds
  LINE_NUM=0
  UPLOAD_SUCCESS=true
  
  # ===== Read file line by line =====
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    LINE_NUM=$((LINE_NUM + 1))
    TIMESTAMP=$((BASE_TIMESTAMP + LINE_NUM))
    
    # Prefix each line with the block file name
    PREFIXED_LINE="[$BLOCK_NAME] $line"
    MESSAGE=$(echo "$PREFIXED_LINE" | jq -Rs .)
    
    # Check size limit
    if [ ${#MESSAGE} -gt $MAX_EVENT_SIZE ]; then
      MESSAGE=$(echo "$PREFIXED_LINE" | head -c 200000 | jq -Rs .)
      MESSAGE="${MESSAGE} [TRUNCATED]"
    fi
    
    # Add to batch
    if [ $BATCH_COUNT -gt 0 ]; then
      EVENT_BATCH+=","
    fi
    EVENT_BATCH+="{\"timestamp\":${TIMESTAMP},\"message\":${MESSAGE}}"
    BATCH_COUNT=$((BATCH_COUNT + 1))
    
    # ===== Send batch when full =====
    if [ $BATCH_COUNT -ge $MAX_BATCH_SIZE ]; then
      EVENT_BATCH+="]"
      
      if [ -n "$SEQUENCE_TOKEN" ] && [ "$SEQUENCE_TOKEN" != "None" ]; then
        RESP=$(aws logs put-log-events \
          --region "$REGION" \
          --log-group-name "$LOG_GROUP" \
          --log-stream-name "$STREAM_NAME" \
          --log-events "$EVENT_BATCH" \
          --sequence-token "$SEQUENCE_TOKEN" \
          --output json 2>/dev/null)
      else
        RESP=$(aws logs put-log-events \
          --region "$REGION" \
          --log-group-name "$LOG_GROUP" \
          --log-stream-name "$STREAM_NAME" \
          --log-events "$EVENT_BATCH" \
          --output json 2>/dev/null)
      fi
      
      # Check if upload was successful
      if [ $? -ne 0 ]; then
        echo "   ⚠️  Upload failed for $BLOCK_NAME"
        UPLOAD_SUCCESS=false
        break
      fi
      
      SEQUENCE_TOKEN=$(echo "$RESP" | jq -r '.nextSequenceToken // empty')
      TOTAL_EVENTS=$((TOTAL_EVENTS + BATCH_COUNT))
      
      EVENT_BATCH="["
      BATCH_COUNT=0
    fi
  done < "$blockfile"
  
  # ===== Send remaining events =====
  if [ $BATCH_COUNT -gt 0 ] && [ "$UPLOAD_SUCCESS" = true ]; then
    EVENT_BATCH+="]"
    
    if [ -n "$SEQUENCE_TOKEN" ] && [ "$SEQUENCE_TOKEN" != "None" ]; then
      RESP=$(aws logs put-log-events \
        --region "$REGION" \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name "$STREAM_NAME" \
        --log-events "$EVENT_BATCH" \
        --sequence-token "$SEQUENCE_TOKEN" \
        --output json 2>/dev/null)
    else
      RESP=$(aws logs put-log-events \
        --region "$REGION" \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name "$STREAM_NAME" \
        --log-events "$EVENT_BATCH" \
        --output json 2>/dev/null)
    fi
    
    # Check if upload was successful
    if [ $? -ne 0 ]; then
      echo "   ⚠️  Upload failed for $BLOCK_NAME"
      UPLOAD_SUCCESS=false
    else
      TOTAL_EVENTS=$((TOTAL_EVENTS + BATCH_COUNT))
    fi
  fi
  
  # ===== Mark as processed and optionally purge =====
  if [ "$UPLOAD_SUCCESS" = true ]; then
    # Add to tracking file
    echo "${FILE_IDENTIFIER}" >> "$TRACKING_FILE"
    
    # Purge the file if enabled
    if [ "$PURGE_AFTER_UPLOAD" = "true" ]; then
      rm -f "$blockfile"
      if [ $? -eq 0 ]; then
        echo "   🗑️  Purged: $BLOCK_NAME"
        PURGED_FILES=$((PURGED_FILES + 1))
      else
        echo "   ⚠️  Failed to purge: $BLOCK_NAME"
      fi
    fi
  fi
done

# ===== Summary =====
echo ""
echo "📊 Summary:"
echo "   ✅ Uploaded: $TOTAL_EVENTS events from $TOTAL_FILES files"
if [ $SKIPPED_FILES -gt 0 ]; then
  echo "   ⏭️  Skipped: $SKIPPED_FILES already-processed files"
fi
if [ $PURGED_FILES -gt 0 ]; then
  echo "   🗑️  Purged: $PURGED_FILES files"
fi
if [ $TOTAL_EVENTS -gt 0 ]; then
  echo "   🔗 View logs: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#logsV2:log-groups/log-group/${LOG_GROUP}"
fi

exit 0  # Always exit successfully





















#!/bin/bash
set -euo pipefail

# ===== Configuration =====
RUN_ID=${GITHUB_RUN_ID:-"manual-$(date +%s)"}
JOB_NAME=${GITHUB_JOB:-"unknown"}
REPO_NAME=${GITHUB_REPOSITORY:-"unknown-repo"}
RUNNER_NAME=${RUNNER_NAME:-$(hostname)}
LOG_GROUP="${LOG_GROUP_NAME:-githubrunnerlogs}"
BLOCKS_DIR="/actions-runner/_diag/blocks"
REGION="${AWS_REGION:-us-east-2}"
MAX_BATCH_SIZE=10
MAX_EVENT_SIZE=262144
# How many minutes back to look for new files (adjust based on job duration)
TIME_WINDOW=${LOG_TIME_WINDOW:-10}

echo "🪵 [POST-JOB] Streaming runner logs to CloudWatch"
echo "   Runner: $RUNNER_NAME"
echo "   Run ID: $RUN_ID"
echo "   Job: $JOB_NAME"
echo "   Repository: $REPO_NAME"
echo "   Time window: Last $TIME_WINDOW minutes"

# ===== Dependency Check =====
if ! command -v aws &> /dev/null; then
  echo "⚠️ Warning: aws cli not found, skipping log upload"
  exit 0
fi

if ! command -v jq &> /dev/null; then
  echo "⚠️ Warning: jq not found, skipping log upload"
  exit 0
fi

# ===== Verify AWS credentials =====
if ! aws sts get-caller-identity --region "$REGION" &> /dev/null; then
  echo "⚠️ Warning: AWS credentials not configured, skipping log upload"
  exit 0
fi

# ===== Check blocks directory =====
if [ ! -d "$BLOCKS_DIR" ]; then
  echo "ℹ️ No blocks directory found at $BLOCKS_DIR, nothing to upload"
  exit 0
fi

# ===== Find ONLY the most recently created/modified files =====
# This looks for files modified in the last N minutes (default 5)
RECENT_BLOCKS=$(find "$BLOCKS_DIR" -type f -mmin -${TIME_WINDOW} 2>/dev/null | sort -t/ -k1 || true)

if [ -z "$RECENT_BLOCKS" ]; then
  echo "ℹ️ No files modified in the last $TIME_WINDOW minutes"
  exit 0
fi

TOTAL_EVENTS=0
TOTAL_FILES=0

# ===== Create log stream name =====
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STREAM_NAME="${RUNNER_NAME}/${REPO_NAME//\//-}/${RUN_ID}/${JOB_NAME}/${TIMESTAMP}"

echo "📤 Creating log stream: $STREAM_NAME"

# ===== Create log stream =====
aws logs create-log-stream \
  --region "$REGION" \
  --log-group-name "$LOG_GROUP" \
  --log-stream-name "$STREAM_NAME" 2>/dev/null || true

# ===== Get sequence token =====
SEQUENCE_TOKEN=$(aws logs describe-log-streams \
  --region "$REGION" \
  --log-group-name "$LOG_GROUP" \
  --log-stream-name-prefix "$STREAM_NAME" \
  --max-items 1 \
  --query "logStreams[?logStreamName=='$STREAM_NAME'].uploadSequenceToken" \
  --output text 2>/dev/null || echo "")

# ===== Process block files =====
for blockfile in $RECENT_BLOCKS; do
  [ -f "$blockfile" ] || continue
  
  BLOCK_NAME=$(basename "$blockfile")
  echo "   📄 Processing: $BLOCK_NAME"
  
  TOTAL_FILES=$((TOTAL_FILES + 1))
  EVENT_BATCH="["
  BATCH_COUNT=0
  
  # Get file modification time for base timestamp
  BASE_TIMESTAMP=$(stat -c %Y "$blockfile" 2>/dev/null || date +%s)
  BASE_TIMESTAMP=$((BASE_TIMESTAMP * 1000))  # Convert to milliseconds
  LINE_NUM=0
  
  # ===== Read file line by line =====
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    LINE_NUM=$((LINE_NUM + 1))
    TIMESTAMP=$((BASE_TIMESTAMP + LINE_NUM))
    
    # Prefix each line with the block file name
    PREFIXED_LINE="[$BLOCK_NAME] $line"
    MESSAGE=$(echo "$PREFIXED_LINE" | jq -Rs .)
    
    # Check size limit
    if [ ${#MESSAGE} -gt $MAX_EVENT_SIZE ]; then
      MESSAGE=$(echo "$PREFIXED_LINE" | head -c 200000 | jq -Rs .)
      MESSAGE="${MESSAGE} [TRUNCATED]"
    fi
    
    # Add to batch
    if [ $BATCH_COUNT -gt 0 ]; then
      EVENT_BATCH+=","
    fi
    EVENT_BATCH+="{\"timestamp\":${TIMESTAMP},\"message\":${MESSAGE}}"
    BATCH_COUNT=$((BATCH_COUNT + 1))
    
    # ===== Send batch when full =====
    if [ $BATCH_COUNT -ge $MAX_BATCH_SIZE ]; then
      EVENT_BATCH+="]"
      
      if [ -n "$SEQUENCE_TOKEN" ] && [ "$SEQUENCE_TOKEN" != "None" ]; then
        RESP=$(aws logs put-log-events \
          --region "$REGION" \
          --log-group-name "$LOG_GROUP" \
          --log-stream-name "$STREAM_NAME" \
          --log-events "$EVENT_BATCH" \
          --sequence-token "$SEQUENCE_TOKEN" \
          --output json 2>/dev/null || echo '{}')
      else
        RESP=$(aws logs put-log-events \
          --region "$REGION" \
          --log-group-name "$LOG_GROUP" \
          --log-stream-name "$STREAM_NAME" \
          --log-events "$EVENT_BATCH" \
          --output json 2>/dev/null || echo '{}')
      fi
      
      SEQUENCE_TOKEN=$(echo "$RESP" | jq -r '.nextSequenceToken // empty')
      TOTAL_EVENTS=$((TOTAL_EVENTS + BATCH_COUNT))
      
      EVENT_BATCH="["
      BATCH_COUNT=0
    fi
  done < "$blockfile"
  
  # ===== Send remaining events =====
  if [ $BATCH_COUNT -gt 0 ]; then
    EVENT_BATCH+="]"
    
    if [ -n "$SEQUENCE_TOKEN" ] && [ "$SEQUENCE_TOKEN" != "None" ]; then
      RESP=$(aws logs put-log-events \
        --region "$REGION" \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name "$STREAM_NAME" \
        --log-events "$EVENT_BATCH" \
        --sequence-token "$SEQUENCE_TOKEN" \
        --output json 2>/dev/null || echo '{}')
    else
      RESP=$(aws logs put-log-events \
        --region "$REGION" \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name "$STREAM_NAME" \
        --log-events "$EVENT_BATCH" \
        --output json 2>/dev/null || echo '{}')
    fi
    
    TOTAL_EVENTS=$((TOTAL_EVENTS + BATCH_COUNT))
  fi
done

if [ $TOTAL_EVENTS -gt 0 ]; then
  echo "✅ Uploaded $TOTAL_EVENTS events from $TOTAL_FILES block files"
  echo "   View logs: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#logsV2:log-groups/log-group/${LOG_GROUP}"
else
  echo "ℹ️ No log events to upload"
fi

exit 0  # Always exit successfully

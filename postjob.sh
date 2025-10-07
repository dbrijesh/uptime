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

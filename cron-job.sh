#!/bin/bash

# Daily Lead Processing Cron Job
# Add to crontab: 0 9 * * * /path/to/cron-job.sh

# Configuration
SCRIPT_DIR="/path/to/your/project"
PYTHON_PATH="/usr/bin/python3"
DOWNLOAD_DIR="/path/to/retran/downloads"
LOG_FILE="/path/to/logs/lead_processing.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log start time
echo "$(date): Starting daily lead processing" >> "$LOG_FILE"

# Change to script directory
cd "$SCRIPT_DIR"

# Find today's Retran file
TODAY=$(date +%Y%m%d)
RETRAN_FILE=$(find "$DOWNLOAD_DIR" -name "*$TODAY*" -type f | head -1)

if [ -z "$RETRAN_FILE" ]; then
    echo "$(date): No Retran file found for today" >> "$LOG_FILE"
    exit 1
fi

echo "$(date): Processing file: $RETRAN_FILE" >> "$LOG_FILE"

# Run the lead processor
$PYTHON_PATH lead_processor.py "$RETRAN_FILE" >> "$LOG_FILE" 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "$(date): Lead processing completed successfully" >> "$LOG_FILE"
else
    echo "$(date): Lead processing failed with error code $?" >> "$LOG_FILE"
    
    # Send alert email (optional)
    echo "Lead processing failed on $(date). Check logs at $LOG_FILE" | \
    mail -s "ALERT: Lead Processing Failed" help@stopforeclosurefast.com
fi

echo "$(date): Lead processing job finished" >> "$LOG_FILE"
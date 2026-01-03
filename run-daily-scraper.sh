#!/bin/bash
# Daily NOD Lead Collection Script
# Run this script to collect NOD leads from LA County and Riverside County

cd /Users/jumaanebey/Documents/stop-foreclosure-fast
source venv/bin/activate

echo "Starting NOD Lead Collection..."
echo "Date: $(date)"
echo "================================"

# Run collection for both counties
python3 scrapers/daily_collection.py --all --days 7

echo "================================"
echo "Collection complete!"

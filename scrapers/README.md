# California NOD Scraper System

A Python-based system for collecting Notice of Default (NOD) and foreclosure leads from California county recorder offices, enriching them with property assessor data, and syncing to Google Sheets for lead tracking.

## Overview

This system automates the collection of pre-foreclosure leads by:

1. **Scraping NOD records** from LA County and Riverside County recorder portals
2. **Enriching leads** with property data from county assessor portals (owner info, property value, etc.)
3. **Deduplicating** records to avoid duplicate entries
4. **Syncing to Google Sheets** for CRM-style lead management
5. **Skip tracing** to find owner contact information (phone, email)

## Scrapers

| Script | Purpose | Data Source |
|--------|---------|-------------|
| `daily_collection.py` | **Main entry point** - orchestrates all scrapers | All sources |
| `la_county_recorder.py` | Scrapes NOD filings from LA County | LA County Registrar-Recorder |
| `riverside_recorder.py` | Scrapes NOD filings from Riverside County | Riverside County WebSelfService |
| `property_enricher.py` | Enriches records with assessor data | LA/Riverside County Assessors |
| `la_county_assessor.py` | LA County property lookups | LA County Assessor Portal |
| `zillow_scraper.py` | Scrapes foreclosure listings | Zillow.com |
| `propertyshark_scraper.py` | Scrapes pre-foreclosure listings | PropertyShark.com |
| `google_sheets_sync.py` | Syncs data to Google Sheets | Google Sheets API |
| `skip_tracer.py` | Automated skip tracing (finds contact info) | TruePeopleSearch |
| `skip_trace_assisted.py` | Semi-automated skip tracing (handles CAPTCHAs) | TruePeopleSearch |
| `export_for_skip_trace.py` | Exports leads for manual skip tracing | Google Sheets |

### Core Modules

| Module | Purpose |
|--------|---------|
| `base_scraper.py` | Base class with HTTP session management, rate limiting, retries, Google Sheets integration |
| `__init__.py` | Package exports and documentation |

## Setup

### Prerequisites

- Python 3.10+ recommended
- Google Chrome browser (for Selenium scrapers)
- Google Cloud service account with Sheets API access

### Installation

```bash
# Navigate to scrapers directory
cd scrapers/

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Google Sheets Configuration

1. Create a Google Cloud project and enable the Sheets API
2. Create a service account and download the credentials JSON
3. Save credentials as `credentials.json` in the project root (parent of scrapers/)
4. Share your Google Sheet with the service account email
5. Copy `.env.example` to `.env` and update the sheet ID

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
```

## Usage Examples

### Daily Collection (Main Script)

```bash
# Collect from all counties (LA + Riverside)
python daily_collection.py --all

# Collect from LA County only
python daily_collection.py --county la

# Collect from Riverside County only
python daily_collection.py --county riverside

# Collect and enrich with assessor data
python daily_collection.py --all --enrich

# Look back 14 days instead of default 7
python daily_collection.py --all --days 14

# Test mode (no writes to Google Sheets)
python daily_collection.py --all --test

# Save results to JSON file
python daily_collection.py --all --output results.json
```

### Individual County Scrapers

```bash
# LA County Recorder
python la_county_recorder.py --days 7
python la_county_recorder.py --test
python la_county_recorder.py --output la_records.json

# Riverside County Recorder
python riverside_recorder.py --days 7
python riverside_recorder.py --test
```

### Property Enrichment

```bash
# Look up property by APN
python property_enricher.py --apn "1234-567-890" --county la

# Look up property by address
python property_enricher.py --address "123 Main St, Los Angeles, CA" --county la

# Test mode
python property_enricher.py --test
```

### Zillow Foreclosure Scraper

```bash
# Scrape LA County foreclosures
python zillow_scraper.py --county "Los Angeles" --pages 3

# Scrape Riverside County foreclosures
python zillow_scraper.py --county "Riverside" --pages 2
```

### Skip Tracing

```bash
# Trace a single address
python skip_tracer.py --address "123 Main St, Los Angeles, CA"

# Trace addresses from Google Sheet (up to 5)
python skip_tracer.py --from-sheet --limit 5

# Trace and update Google Sheet with results
python skip_tracer.py --from-sheet --limit 5 --update-sheet

# Semi-automated (you handle CAPTCHAs)
python skip_trace_assisted.py

# Export leads for manual skip tracing
python export_for_skip_trace.py --limit 25
python export_for_skip_trace.py --high-value  # Only $400k+ properties
```

### Google Sheets Sync

```bash
# List existing records
python google_sheets_sync.py --list

# Test sync with a dummy record
python google_sheets_sync.py --test
```

### Cron Setup (Automated Daily Collection)

```bash
# Add to crontab (run daily at 6 AM)
0 6 * * * /path/to/venv/bin/python /path/to/scrapers/daily_collection.py --all --enrich
```

## Google Sheets Integration

### Sheet Structure

The system expects the following columns in your Google Sheet:

| Column | Field | Description |
|--------|-------|-------------|
| A | lead_id | Unique identifier (auto-generated) |
| B | date_found | Date the lead was discovered |
| C | recording_date | NOD recording date |
| D | days_since_nod | Days since NOD was filed |
| E | owner_name | Property owner / trustor name |
| F | phone | Contact phone number |
| G | email | Contact email address |
| H | property_address | Full property address |
| I | city | City |
| J | county | County name |
| K | apn | Assessor Parcel Number |
| L | estimated_value | Estimated property value |
| M | mortgage_balance | Outstanding mortgage amount |
| N | equity | Calculated equity |
| O | lender | Lender / beneficiary |
| P | trustee | Trustee |
| Q | auction_date | Scheduled auction date |
| R | days_to_auction | Days until auction |
| S | stage | NOD / NTS / Auction / Sold |
| T | status | New / Contacted / Closed |
| U | lead_score | Priority ranking |
| V | notes | Additional notes |
| W | source | Data source |

### Deduplication

Records are deduplicated based on:
1. APN + Recording Date (primary)
2. Property Address (fallback)

Duplicate records are automatically skipped during sync.

## Rate Limiting

All scrapers include built-in rate limiting to avoid being blocked:

- Default: 2-3 seconds between requests
- Property enrichment: 5 seconds between requests
- Skip tracing: 10+ seconds between requests

## Error Handling

- Logs are written to `/tmp/nod_scraper.log`
- Failed requests are automatically retried (up to 3 times)
- Individual record failures don't stop the entire batch
- Results include error statistics

## Programmatic Usage

```python
from scrapers import run_daily_collection, DailyNODCollector

# Quick run
stats = run_daily_collection(
    counties=['la', 'riverside'],
    days_back=7,
    enrich=True
)

# Or with more control
collector = DailyNODCollector(test_mode=False)
stats = collector.run_full_collection(
    counties=['la'],
    days_back=14,
    enrich=True,
    max_enrich=50
)
print(stats)
```

## Troubleshooting

### Chrome WebDriver Issues

```bash
# Update webdriver-manager cache
pip install --upgrade webdriver-manager

# Or manually specify Chrome location
export CHROME_BINARY=/path/to/chrome
```

### Google Sheets Authentication

```bash
# Verify credentials file exists
ls -la ../credentials.json

# Check service account permissions
# Make sure the service account email has edit access to the sheet
```

### Rate Limit Errors

If you're getting blocked:
1. Increase rate_limit_seconds in scraper initialization
2. Reduce the number of records per run
3. Use `--test` mode to verify without hitting live servers

## Project Structure

```
scrapers/
├── __init__.py              # Package exports
├── base_scraper.py          # Base class and utilities
├── daily_collection.py      # Main entry point
├── la_county_recorder.py    # LA County NOD scraper
├── riverside_recorder.py    # Riverside County NOD scraper
├── la_county_assessor.py    # LA County assessor lookup
├── property_enricher.py     # Property data enrichment
├── google_sheets_sync.py    # Google Sheets sync
├── zillow_scraper.py        # Zillow foreclosure scraper
├── propertyshark_scraper.py # PropertyShark scraper
├── skip_tracer.py           # Automated skip tracing
├── skip_trace_assisted.py   # Semi-automated skip tracing
├── export_for_skip_trace.py # Export for manual skip tracing
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── README.md                # This file
```

## License

Private - Internal use only.

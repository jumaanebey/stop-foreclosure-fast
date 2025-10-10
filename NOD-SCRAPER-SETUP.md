# NOD Lead Scraper - Setup Instructions

## What This Does

Automatically imports foreclosure leads (Notice of Default) into your Google Sheet for tracking and calling.

## Quick Setup (10 minutes)

### Step 1: Install Python (if not installed)

**Mac:**
```bash
# Check if Python is installed
python3 --version

# If not installed, install via Homebrew
brew install python3
```

**Already installed?** Skip to Step 2.

### Step 2: Install Required Libraries

```bash
cd /Users/jumaanebey/Documents/stop-foreclosure-fast
pip3 install requests beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Set Up Google Sheets API Access

**A. Create Google Cloud Project:**

1. Go to: https://console.cloud.google.com/
2. Click "Create Project"
3. Name it: "Foreclosure Leads"
4. Click "Create"

**B. Enable Google Sheets API:**

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"

**C. Create Service Account:**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Name: "Lead Scraper"
4. Click "Create and Continue"
5. Skip "Grant this service account access" (click Continue)
6. Skip "Grant users access" (click Done)

**D. Download Credentials:**

1. Click on the service account email you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON"
5. Download the file
6. Rename it to `credentials.json`
7. Move it to: `/Users/jumaanebey/Documents/stop-foreclosure-fast/credentials.json`

**E. Share Your Google Sheet:**

1. Open `credentials.json` and find the "client_email" field
2. Copy that email (looks like: `lead-scraper@foreclosure-leads-xxxxx.iam.gserviceaccount.com`)
3. Go to your Google Sheet: https://docs.google.com/spreadsheets/d/1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw/edit
4. Click "Share"
5. Paste the service account email
6. Give it "Editor" access
7. Click "Send" (uncheck "Notify people")

### Step 4: Create "NOD Leads" Tab in Google Sheet

1. Open your Google Sheet
2. Click the "+" at the bottom to add a new tab
3. Name it exactly: `NOD Leads`
4. The script will automatically create the column headers

### Step 5: Test the Script

```bash
cd /Users/jumaanebey/Documents/stop-foreclosure-fast
python3 nod-lead-scraper.py
```

You should see:
```
✅ Connected to Google Sheets
✅ Created headers in 'NOD Leads' tab
✅ Added lead: 123 Test St, Los Angeles, CA 90001
```

Check your Google Sheet - you should see a test lead. **Delete this test row.**

---

## How to Use

### Option 1: Import from CSV (Recommended)

If you have a CSV file with foreclosure data (from ForeclosureRadar, RealtyTrac, etc.):

```bash
python3 nod-lead-scraper.py import your-nod-data.csv
```

**CSV Format:**
```
Property Address,Owner Name,Recording Date,Lender,Estimated Value
123 Main St Los Angeles CA 90001,John Smith,2025-01-15,Wells Fargo,450000
456 Oak Ave San Diego CA 92101,Jane Doe,2025-01-14,Bank of America,380000
```

The script will automatically:
- Import all leads
- Calculate "Days Since NOD"
- Add to your Google Sheet
- Set status to "New"

### Option 2: Manual Collection + Sheet Entry

1. Visit LA County Recorder: https://www.lavote.gov/home/recorder
2. Search for Notice of Default filings
3. Manually add to Google Sheet
4. Use the sheet to track calls and status

### Option 3: Subscribe to Data Service (Best Long-Term)

**ForeclosureRadar.com** ($100-300/month):
1. Sign up at https://www.foreclosureradar.com/
2. Filter for California > Los Angeles County
3. Export daily NODs as CSV
4. Run: `python3 nod-lead-scraper.py import foreclosure-radar-export.csv`
5. Start calling!

**ROI:** If you close 1 deal per month ($5,000+), the $200/month subscription pays for itself 25x over.

---

## Google Sheet Structure

The script creates these columns in "NOD Leads" tab:

| Column | Purpose | Filled By |
|--------|---------|-----------|
| Date Found | When you found this lead | Script (auto) |
| Property Address | Full address | Script from CSV |
| Owner Name | Homeowner name | Script from CSV |
| Phone Number | Contact phone | You (skip trace) |
| Email | Contact email | You (skip trace) |
| Recording Date | Date NOD was filed | Script from CSV |
| Days Since NOD | How long ago | Script (auto calculated) |
| County | Which county | Script (default: LA) |
| Estimated Value | Home value | Script from CSV or Zillow |
| Lender | Bank name | Script from CSV |
| Status | New/Called/Contacted/etc | You (update as you work) |
| Last Contact | Last time you called | You |
| Next Follow-up Date | When to call again | You |
| Notes | Your notes | You |

---

## Workflow

**Daily Routine:**

1. **Get New Leads (Morning):**
   ```bash
   # If you have CSV from ForeclosureRadar
   python3 nod-lead-scraper.py import today-nods.csv
   ```

2. **Skip Trace Phone Numbers:**
   - Export "New" leads from Google Sheet
   - Upload to BatchSkipTracing.com ($0.15/lead)
   - Get back phone numbers
   - Import back to sheet

3. **Make Calls (Afternoon):**
   - Filter sheet for "New" status
   - Call using script from FORECLOSURE-LEAD-FARMING-GUIDE.md
   - Update status as you go:
     - "Called - No Answer"
     - "Called - Left VM"
     - "Contacted - Appointment Set"
     - "Contacted - Not Interested"
     - "Closed - Deal Won"

4. **Follow Up:**
   - Check "Next Follow-up Date" column
   - Call anyone due for follow-up
   - Send free guide PDF to interested leads

---

## Troubleshooting

**Error: "credentials.json not found"**
- Make sure you downloaded the JSON key file from Google Cloud
- Rename it to exactly `credentials.json`
- Place it in `/Users/jumaanebey/Documents/stop-foreclosure-fast/`

**Error: "Unable to parse range"**
- Create a tab named exactly `NOD Leads` in your Google Sheet
- Make sure there are no extra spaces

**Error: "The caller does not have permission"**
- Open your credentials.json
- Copy the "client_email" value
- Share your Google Sheet with that email address (Editor access)

**No leads imported from CSV:**
- Check CSV column names match expected format
- Make sure CSV has headers in first row
- Try opening CSV in Excel to verify format

**Script runs but nothing in Google Sheet:**
- Check if "NOD Leads" tab exists
- Verify service account has Editor access
- Check Google Sheet ID in script matches your sheet

---

## Advanced: Schedule Automatic Daily Import

**Mac: Use cron to run daily**

1. Edit crontab:
   ```bash
   crontab -e
   ```

2. Add this line (runs every day at 9 AM):
   ```
   0 9 * * * cd /Users/jumaanebey/Documents/stop-foreclosure-fast && /usr/local/bin/python3 nod-lead-scraper.py import /path/to/daily-nods.csv >> /tmp/nod-scraper.log 2>&1
   ```

3. Save and exit

**Pair with ForeclosureRadar:**
- Set up ForeclosureRadar to email you daily CSV
- Save CSV to specific folder
- Script auto-imports every morning
- You wake up to fresh leads every day

---

## Cost Breakdown

**Free Approach:**
- Python script: $0
- Google Sheets: $0
- Manual lead collection: $0
- Time: 2-3 hours/day
- Leads: 25-50/day

**Paid Approach (Recommended):**
- ForeclosureRadar: $200/month
- Skip tracing: $15-30/month (100-200 leads × $0.15)
- Total: ~$230/month
- Time: 30 min/day (just import CSV)
- Leads: 500-1000/month
- **ROI: 1 deal pays for 22-78 months of subscriptions**

---

## Next Steps

1. **Today:** Set up Google Sheets API (10 min)
2. **This Week:** Collect your first 50 leads manually, test calling
3. **After First Deal:** Subscribe to ForeclosureRadar, automate everything
4. **Scale:** Hire VA to make calls, you focus on consultations

Need help? See FORECLOSURE-LEAD-FARMING-GUIDE.md for calling scripts and strategies.

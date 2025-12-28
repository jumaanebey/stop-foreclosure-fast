# Claude for Chrome - NOD Lead Scraper Workflows

Use Claude for Chrome to extract NOD (Notice of Default) leads from these sources and add them to your Google Sheet.

**Your Google Sheet:** https://docs.google.com/spreadsheets/d/1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw/edit

---

## Source 1: PropertyShark (Free - Limited Searches)

### LA County
**URL:** https://www.propertyshark.com/mason/ca/Los-Angeles-County/Foreclosures

### Riverside County
**URL:** https://www.propertyshark.com/mason/ca/Riverside-County/Foreclosures

### Steps:
1. Go to the URL above
2. Filter for "Pre-Foreclosure" or "Notice of Default"
3. Open Claude for Chrome and use this prompt:

```
Extract all pre-foreclosure/NOD properties from this page.

For each property, get:
- Full property address
- City
- Owner name (if shown)
- Filing/Recording date
- Estimated value (if shown)
- Lender (if shown)

Format as a table with columns:
Address | Owner Name | Recording Date | City | County | Estimated Value | Lender | Notes

Set County to "Los Angeles" or "Riverside" based on the page.
Set Notes to "PropertyShark"
```

---

## Source 2: Riverside County Official Records

**URL:** https://webselfservice.riversideacr.com/Web/action/ACTIONGROUP2111S1

### Steps:
1. Go to the URL above
2. Select **"Document Type Search - Web"**
3. Choose document type: **"Notice of Default"** or **"NOD"**
4. Set date range: Last 7-30 days
5. Click Search
6. Open Claude for Chrome and use this prompt:

```
Extract all Notice of Default records from this search results page.

For each record, get:
- Document number
- Recording date
- Grantor name (property owner)
- Property address (if shown)
- Grantee/Beneficiary (lender)

Format as a table with columns:
Address | Owner Name | Recording Date | City | County | Estimated Value | Lender | Notes

Set County to "Riverside"
Set Notes to "Riverside County Recorder"
If no address shown, put the document number in Notes so I can look it up.
```

### Note on Riverside County:
- Copy fees: $7 first page, $1 each additional page
- Some records may only show document numbers - you may need to click into each to get property details

---

## Source 3: LA County Official Records

**URL:** https://datastore.netronline.com/losangeles

### Search Options:
- By Name (Grantor/Grantee)
- By AIN (Assessor's Identification Number)
- By Document Number

### Steps:
1. Go to the URL above
2. Search by document type if available, or search recent recordings
3. Filter for "Notice of Default" documents
4. Open Claude for Chrome and use this prompt:

```
Extract all Notice of Default records from this page.

For each record, get:
- Document number
- Recording date
- Grantor name (this is the property owner)
- Grantee name (this is the lender)
- Property address or AIN

Format as a table with columns:
Address | Owner Name | Recording Date | City | County | Estimated Value | Lender | Notes

Set County to "Los Angeles"
Set Notes to "LA County Recorder"
```

### Alternative LA County Method:
**Public Records Request Portal:** https://lacountyrrcc.nextrequest.com/

You can submit a public records request for all NODs recorded in the past week. This is free but takes 1-3 business days.

---

## Adding Leads to Google Sheet

After extracting data from any source, open your Google Sheet and give Claude this prompt:

```
Add these leads to my Google Sheet. Format each row with:

A: Date Found = today's date (2024-XX-XX format)
B: Recording Date = from the data
C: Owner Name = from the data
D: Phone Number = leave blank
E: Email = leave blank
F: Property Address = from the data
G: City = from the data
H: County = Los Angeles or Riverside
I: Estimated Value = from the data (or blank)
J: Mortgage Balance = leave blank
K: Equity = leave blank
L: Auction Date = leave blank
M: Status = "New"
N: Lead Score = leave blank
O: Notes = source (PropertyShark, LA County Recorder, etc.)
P: Last Contact = leave blank
Q: Email Sent Date = leave blank

Here are the leads to add:
[PASTE YOUR EXTRACTED TABLE HERE]
```

---

## Alternative: Use Python Import Script

If you prefer, save the extracted data as a CSV file and use the import script:

```bash
cd /Users/jumaanebey/Documents/stop-foreclosure-fast
source venv/bin/activate
python3 nod-lead-scraper.py import your-leads.csv
```

CSV format should have headers:
```
Address,Owner Name,Recording Date,City,County,Estimated Value,Lender,Notes
```

---

## Weekly Workflow Schedule

| Day | Task | Time |
|-----|------|------|
| Monday | Scrape LA County (PropertyShark + Official) | 15 min |
| Wednesday | Scrape Riverside County (PropertyShark + Official) | 15 min |
| Friday | Skip trace new leads for phone/email | 20 min |

---

## Skip Tracing (Finding Contact Info)

After you have property addresses and owner names, you need phone numbers and emails.

### Free Skip Tracing:
Use Claude for Chrome on these sites:

1. **TruePeopleSearch.com** - Search by name + city
2. **FastPeopleSearch.com** - Similar results
3. **Whitepages.com** - Limited free searches

### Claude Prompt for Skip Tracing:
```
I need to find contact info for these property owners.

For each person, search TruePeopleSearch.com using their name and city.
Get their:
- Phone number(s)
- Email address (if available)

Here are the owners to search:
[PASTE OWNER NAMES AND CITIES]

Format results as:
Name | Phone | Email
```

### Paid Skip Tracing (faster, more accurate):
- BatchSkipTracing.com - $0.15/record
- SkipGenie.com - $0.12/record
- REISkip.com - $0.18/record

---

## What Happens After Leads Are Added

Once leads are in your Google Sheet with email addresses:

1. **n8n checks every 15 minutes** for new leads with Status = "New"
2. **Sends initial email** automatically
3. **Updates Status** to "Email Sent"
4. **48 hours later** sends follow-up email
5. **Updates Status** to "Follow-up Sent"
6. **Daily at 8 AM** you get a summary report

---

## Quick Reference

| Source | URL | Cost |
|--------|-----|------|
| PropertyShark LA | propertyshark.com/mason/ca/Los-Angeles-County/Foreclosures | Free (limited) |
| PropertyShark Riverside | propertyshark.com/mason/ca/Riverside-County/Foreclosures | Free (limited) |
| Riverside County Recorder | webselfservice.riversideacr.com | $7/doc copy |
| LA County Records | datastore.netronline.com/losangeles | Free to search |
| LA County Records Request | lacountyrrcc.nextrequest.com | Free |

---

## Troubleshooting

**"Claude can't see the data"**
- Make sure the page is fully loaded
- Scroll down to load all results
- Try refreshing the page

**"No results found"**
- Try a broader date range
- Check spelling of document type
- Some counties use "NOD" vs "Notice of Default"

**"Need to log in"**
- PropertyShark requires free account for some searches
- County portals are usually free without login

---

## Questions?

Your automations are set up. Once leads have email addresses in the Google Sheet, n8n handles the rest automatically.

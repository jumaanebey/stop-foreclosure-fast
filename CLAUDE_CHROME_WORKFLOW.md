# Claude for Chrome - Foreclosure Lead Workflow

## Weekly Lead Collection (15-20 minutes)

---

## STEP 1: Collect LA County Leads

### Open Zillow LA County Foreclosures
**URL:** https://www.zillow.com/los-angeles-county-ca/foreclosures/

### Give Claude for Chrome this prompt:

```
Extract ALL foreclosure properties visible on this page.

For each property, get:
- Full street address
- City
- Price (as shown, e.g., $650,000)
- Bedrooms
- Bathrooms
- Square feet (if shown)

Format as a Google Sheets table with these EXACT columns:
Date Found | Recording Date | Owner Name | Phone Number | Email | Property Address | City | County | Estimated Value | Mortgage Balance | Equity | Auction Date | Status | Lead Score | Notes

Rules:
- Date Found = today's date (2025-12-27)
- Recording Date = leave blank
- Owner Name = leave blank (we'll skip trace later)
- Phone Number = leave blank
- Email = leave blank
- Property Address = the full address
- City = city from address
- County = Los Angeles
- Estimated Value = the price shown
- Mortgage Balance = leave blank
- Equity = leave blank
- Auction Date = leave blank
- Status = New
- Lead Score = leave blank
- Notes = Zillow Foreclosure

Return the data in a format I can copy/paste directly into Google Sheets.
```

### Scroll down and repeat
- Scroll to load more listings
- Ask Claude to extract the new listings
- Repeat until you have 30-50 leads

---

## STEP 2: Collect Riverside County Leads

### Open Zillow Riverside County Foreclosures
**URL:** https://www.zillow.com/riverside-county-ca/foreclosures/

### Use the same prompt, but change County to "Riverside":

```
Extract ALL foreclosure properties visible on this page.

For each property, get:
- Full street address
- City
- Price
- Bedrooms
- Bathrooms

Format as a Google Sheets table with these EXACT columns:
Date Found | Recording Date | Owner Name | Phone Number | Email | Property Address | City | County | Estimated Value | Mortgage Balance | Equity | Auction Date | Status | Lead Score | Notes

Rules:
- Date Found = 2025-12-27
- County = Riverside
- Status = New
- Notes = Zillow Foreclosure
- Leave other fields blank

Return in copy/paste format for Google Sheets.
```

---

## STEP 3: Paste into Google Sheet

### Open your lead tracking sheet:
**URL:** https://docs.google.com/spreadsheets/d/1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw/edit

### Paste the data:
1. Click on the first empty row in column A
2. Paste (Cmd+V or Ctrl+V)
3. The data should fill in all columns correctly

---

## STEP 4: Skip Trace for Phone Numbers

### Open TruePeopleSearch
**URL:** https://www.truepeoplesearch.com

### For each lead that needs a phone number:

1. Copy the **Property Address** from your sheet
2. Search on TruePeopleSearch
3. Look for the property owner's name and phone
4. Ask Claude for Chrome:

```
Find the property owner for this address and their phone number.
Address: [paste address]

Return:
- Owner Name
- Best phone number
- Email (if available)
```

### Batch Skip Tracing (Faster)
Copy 10-15 addresses, then prompt Claude:

```
I need to find owner contact info for these foreclosure properties.
Search TruePeopleSearch for each address.

Addresses:
[paste list of addresses]

For each one, find:
- Property owner name
- Phone number
- Email (if available)

Return as a table:
Address | Owner Name | Phone | Email
```

---

## STEP 5: Update Google Sheet with Contact Info

1. Go back to your Google Sheet
2. For each lead, fill in:
   - Column C: Owner Name
   - Column D: Phone Number
   - Column E: Email

---

## What Happens Next (Automatic)

Once leads have email addresses in the sheet:

1. **n8n checks every 15 minutes** for new leads
2. **Sends initial email** automatically
3. **Updates Status** to "Email Sent"
4. **48 hours later** sends follow-up email
5. **Daily at 8 AM** you get a summary report

---

## Weekly Schedule

| Day | Task | Time |
|-----|------|------|
| Monday | Collect LA County leads from Zillow | 10 min |
| Monday | Collect Riverside County leads from Zillow | 10 min |
| Tuesday | Skip trace Monday's leads | 15 min |
| Thursday | Collect new leads (both counties) | 15 min |
| Friday | Skip trace Thursday's leads | 15 min |

---

## Pro Tips

### 1. Focus on High-Value Properties First
Skip trace properties with higher values first - more equity = better leads

### 2. Check Multiple Pages
Zillow shows ~40 listings per page. Click "Next" and extract from 2-3 pages.

### 3. Filter by Price
On Zillow, set price filters to focus on your target range (e.g., $300k-$800k)

### 4. Use Redfin Too
Redfin also shows foreclosures:
- LA: https://www.redfin.com/county/321/CA/Los-Angeles-County/filter/property-type=house,include=foreclosures
- Riverside: https://www.redfin.com/county/329/CA/Riverside-County/filter/property-type=house,include=foreclosures

Same Claude prompts work on Redfin.

---

## Quick Reference

### Your Google Sheet
https://docs.google.com/spreadsheets/d/1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw/edit

### Zillow Foreclosures
- LA County: https://www.zillow.com/los-angeles-county-ca/foreclosures/
- Riverside: https://www.zillow.com/riverside-county-ca/foreclosures/

### Skip Tracing
- TruePeopleSearch: https://www.truepeoplesearch.com
- FastPeopleSearch: https://www.fastpeoplesearch.com

### Column Order (Google Sheet)
A: Date Found
B: Recording Date
C: Owner Name
D: Phone Number
E: Email
F: Property Address
G: City
H: County
I: Estimated Value
J: Mortgage Balance
K: Equity
L: Auction Date
M: Status
N: Lead Score
O: Notes
P: Last Contact
Q: Email Sent Date

---

## Troubleshooting

**"Claude can't see the listings"**
- Make sure the page is fully loaded
- Scroll down to load all listings first
- Try refreshing the page

**"Data doesn't paste correctly"**
- Make sure Claude formatted it as tab-separated values
- Ask Claude to "format as TSV (tab-separated values)"

**"Can't find owner on TruePeopleSearch"**
- Try searching by just the city + owner name pattern
- Try FastPeopleSearch as an alternative
- Some properties are owned by LLCs/trusts (harder to trace)

---

## Need Help?

If you get stuck, paste the issue into Claude and ask for help.
The n8n automations handle everything once leads are in the sheet with contact info.

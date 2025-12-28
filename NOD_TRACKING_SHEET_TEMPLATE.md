# NOD Lead Tracking Google Sheet Template

## Setup Instructions

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet named "NOD Leads - My Foreclosure Solution"
3. Create the following columns (copy/paste the headers below)

---

## Sheet 1: "NOD Leads" - Column Headers

Copy these headers to Row 1:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Date Found | Recording Date | Owner Name | Phone Number | Email | Property Address | City | County | Estimated Value | Mortgage Balance | Equity | Auction Date | Status | Lead Score | Notes |

---

## Column Definitions

| Column | Description | Data Type | Example |
|--------|-------------|-----------|---------|
| **Date Found** | When you found this NOD | Date | 12/27/2025 |
| **Recording Date** | NOD recording date | Date | 12/20/2025 |
| **Owner Name** | Property owner's name | Text | John Smith |
| **Phone Number** | From skip tracing | Phone | (949) 555-1234 |
| **Email** | From skip tracing | Email | john@email.com |
| **Property Address** | Full address | Text | 123 Main St, Irvine, CA 92618 |
| **City** | City name | Text | Irvine |
| **County** | CA County | Text | Orange |
| **Estimated Value** | Zillow/Redfin estimate | Currency | $750,000 |
| **Mortgage Balance** | From NOD if available | Currency | $500,000 |
| **Equity** | =I2-J2 (formula) | Currency | $250,000 |
| **Auction Date** | Trustee sale date | Date | 3/20/2026 |
| **Status** | Lead status | Dropdown | New |
| **Lead Score** | Auto-calculated | Number | 85 |
| **Notes** | Any notes | Text | Called 12/27, no answer |

---

## Status Dropdown Values

Create a Data Validation dropdown for the Status column with these options:

1. **New** - Just found, not contacted
2. **Contacted** - Initial contact made
3. **No Answer** - Tried calling, no response
4. **Left Voicemail** - Left message
5. **Email Sent** - Email sent, awaiting response
6. **SMS Sent** - Text sent, awaiting response
7. **Callback Scheduled** - They're calling back
8. **Consultation Scheduled** - Meeting booked
9. **Consultation Complete** - Meeting done
10. **Proposal Sent** - Offer sent
11. **Negotiating** - In discussions
12. **Contract Signed** - Deal closed
13. **Not Interested** - Declined
14. **Wrong Number** - Bad contact info
15. **Property Sold** - Already sold

---

## Lead Score Formula

Add this formula to Column N (Lead Score) starting at row 2:

```
=IF(A2="","",
  IFS(
    AND(L2-TODAY()<=7, K2>=100000), 100,
    AND(L2-TODAY()<=7, K2>=50000), 90,
    AND(L2-TODAY()<=7), 80,
    AND(L2-TODAY()<=30, K2>=100000), 85,
    AND(L2-TODAY()<=30, K2>=50000), 75,
    AND(L2-TODAY()<=30), 65,
    AND(L2-TODAY()<=60, K2>=100000), 70,
    AND(L2-TODAY()<=60), 55,
    TRUE, 40
  )
)
```

This scores leads higher when:
- Auction is soon (< 7 days = higher score)
- High equity (> $100K = bonus points)

---

## Sheet 2: "Dashboard" - Key Metrics

Create formulas to track:

| Metric | Formula |
|--------|---------|
| Total Leads | `=COUNTA('NOD Leads'!A:A)-1` |
| New Leads | `=COUNTIF('NOD Leads'!M:M,"New")` |
| Contacted | `=COUNTIF('NOD Leads'!M:M,"Contacted")` |
| Consultations | `=COUNTIF('NOD Leads'!M:M,"Consultation Scheduled")` |
| Deals Closed | `=COUNTIF('NOD Leads'!M:M,"Contract Signed")` |
| Avg Equity | `=AVERAGE('NOD Leads'!K:K)` |
| Hot Leads (Score>80) | `=COUNTIF('NOD Leads'!N:N,">80")` |

---

## Sheet 3: "Follow-up Queue"

Create a filtered view showing leads that need follow-up:

| Column | Description |
|--------|-------------|
| Leads with status "New" older than 1 day |
| Leads with status "Email Sent" older than 2 days |
| Leads with status "No Answer" - need retry |
| Leads with auction in < 14 days |

Formula for "Needs Follow-up":
```
=FILTER('NOD Leads'!A:O,
  ('NOD Leads'!M:M="New")*('NOD Leads'!A:A<TODAY()-1) +
  ('NOD Leads'!M:M="Email Sent")*('NOD Leads'!A:A<TODAY()-2) +
  ('NOD Leads'!L:L-TODAY()<=14)*('NOD Leads'!M:M<>"Contract Signed")
)
```

---

## Conditional Formatting Rules

Apply these to the NOD Leads sheet:

1. **Red background** if Auction Date is within 7 days
   - Range: L:L
   - Formula: `=AND(L1<>"",L1-TODAY()<=7,L1-TODAY()>=0)`

2. **Yellow background** if Auction Date is within 30 days
   - Range: L:L
   - Formula: `=AND(L1<>"",L1-TODAY()<=30,L1-TODAY()>7)`

3. **Green background** for high equity (>$100K)
   - Range: K:K
   - Formula: `=K1>=100000`

4. **Bold text** for Lead Score > 80
   - Range: N:N
   - Formula: `=N1>=80`

---

## Automation with n8n

Connect this sheet to n8n for:

1. **Auto-add new NODs** from scraper
2. **Auto-update phone numbers** from skip tracing
3. **Auto-send emails** when status is "New"
4. **Auto-alert** when lead score > 80

Sheet ID needed for n8n: `[Your Sheet ID here]`

---

## Quick Start Checklist

- [ ] Create new Google Sheet
- [ ] Add "NOD Leads" sheet with headers
- [ ] Add "Dashboard" sheet with formulas
- [ ] Add "Follow-up Queue" filtered view
- [ ] Set up Status dropdown validation
- [ ] Add Lead Score formula
- [ ] Apply conditional formatting
- [ ] Share with your email for n8n access
- [ ] Copy Sheet ID for automation setup

---

**Template Version:** 1.0
**Last Updated:** December 27, 2025

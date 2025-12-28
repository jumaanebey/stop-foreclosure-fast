# Sprint 2: Automation Setup Instructions

Complete these steps in order. Each section takes 10-30 minutes.

---

## STEP 1: Set Up n8n (15 minutes)

### Option A: n8n Cloud (Recommended for beginners)

1. Go to https://n8n.io/cloud
2. Click **"Start Free Trial"**
3. Create account with your email
4. Choose **Free tier** (2,500 executions/month)
5. Your n8n dashboard URL will be: `https://your-name.app.n8n.cloud`

### Option B: Self-Hosted (Free forever, more technical)

```bash
# Install Docker first if you don't have it
# Then run:
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

Access at: http://localhost:5678

---

## STEP 2: Connect Google Sheets to n8n (10 minutes)

1. In n8n, click **Settings** (gear icon) → **Credentials**
2. Click **"Add Credential"**
3. Search for **"Google Sheets API"**
4. Select **"OAuth2"** method
5. Click **"Sign in with Google"**
6. Select your Google account
7. Click **"Allow"** to grant access
8. Name it: `My Foreclosure Google Sheets`
9. Click **"Save"**

---

## STEP 3: Set Up Gmail for Sending Emails (10 minutes)

### Get Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Go to https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other** → Type "n8n"
6. Click **"Generate"**
7. **COPY THE 16-CHARACTER PASSWORD** (you won't see it again)

### Add SMTP Credential in n8n:

1. In n8n → **Settings** → **Credentials**
2. Click **"Add Credential"**
3. Search for **"SMTP"**
4. Enter these values:

| Field | Value |
|-------|-------|
| Host | smtp.gmail.com |
| Port | 587 |
| SSL/TLS | TLS |
| User | your-email@gmail.com |
| Password | [16-char app password from above] |

5. Name it: `Gmail SMTP`
6. Click **"Save"**

---

## STEP 4: Create Your Lead Tracking Google Sheet (10 minutes)

1. Go to https://sheets.google.com
2. Click **"+ Blank"** to create new sheet
3. Name it: **"NOD Leads - My Foreclosure Solution"**
4. In Row 1, add these column headers (copy exactly):

```
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
```

5. **Get your Sheet ID:**
   - Look at the URL: `https://docs.google.com/spreadsheets/d/XXXXXXXXXX/edit`
   - Copy the `XXXXXXXXXX` part (between `/d/` and `/edit`)
   - Save this - you'll need it for n8n

6. **Add Status dropdown (Column M):**
   - Select column M (click the "M" header)
   - Go to **Data** → **Data validation**
   - Criteria: **Dropdown (from a range)**
   - Enter these values (one per line):
     ```
     New
     Email Sent
     SMS Sent
     Contacted
     Callback Scheduled
     Consultation Scheduled
     Proposal Sent
     Contract Signed
     Not Interested
     Wrong Number
     ```
   - Click **"Done"**

---

## STEP 5: Import Email Follow-up Workflow (10 minutes)

1. In n8n, click **"Add Workflow"** (+ button)
2. Click the **menu (⋮)** → **"Import from File"**
3. Navigate to: `/Users/jumaanebey/Documents/stop-foreclosure-fast/n8n-workflows/`
4. Select: `1-email-followup-automation.json`
5. Click **"Import"**

### Configure the workflow:

**Node 1: "Schedule Trigger"**
- Already set to run every 15 minutes
- No changes needed

**Node 2: "Get New Leads from Sheet"**
1. Click on this node
2. Under **Credential**, select your Google Sheets credential
3. Under **Document ID**, paste YOUR Sheet ID from Step 4
4. Sheet Name should be: `Sheet1` (or rename your tab to match)
5. Click **"Save"**

**Node 3: "Filter New Leads"**
- No changes needed

**Node 4: "Send Initial Email"**
1. Click on this node
2. Under **Credential**, select your Gmail SMTP credential
3. Change **From Email** to: `help@myforeclosuresolution.com` (or your email)
4. In the **Text** field, replace `[YOUR NAME]` with your actual name
5. Click **"Save"**

**Node 5: "Update Status in Sheet"**
1. Click on this node
2. Under **Credential**, select your Google Sheets credential
3. Under **Document ID**, paste YOUR Sheet ID
4. Click **"Save"**

### Test the workflow:

1. Add a test row to your Google Sheet:
   ```
   Date Found: [today's date]
   Owner Name: Test User
   Email: your-personal-email@gmail.com
   Property Address: 123 Test St
   Status: New
   ```

2. In n8n, click **"Test Workflow"** (play button)
3. Check your email - you should receive the follow-up email
4. Check Google Sheet - Status should change to "Email Sent"

### Activate the workflow:

1. Click the **"Active"** toggle in top-right corner
2. Toggle should turn green
3. Workflow now runs automatically every 15 minutes

---

## STEP 6: Import Daily Lead Report Workflow (5 minutes)

1. In n8n, click **"Add Workflow"**
2. Import: `2-daily-lead-report.json`
3. Update the Google Sheets credential and Sheet ID (same as before)
4. Update the SMTP credential
5. Change the **To Email** to your email address
6. Click **"Test Workflow"** to receive a test report
7. Activate the workflow

This sends you a daily summary at 8 AM.

---

## STEP 7: Set Up Twilio for SMS (Optional - 15 minutes)

Skip this if you don't want SMS follow-ups.

### Create Twilio Account:

1. Go to https://www.twilio.com/try-twilio
2. Sign up with email
3. Verify your phone number
4. Complete signup

### Get a Phone Number:

1. In Twilio Console, go to **Phone Numbers** → **Buy a Number**
2. Search for a number with your area code (949)
3. Click **"Buy"** (~$1.15/month)
4. Copy your new Twilio phone number

### Get API Credentials:

1. Go to Twilio Console **Dashboard**
2. Copy your **Account SID**
3. Copy your **Auth Token** (click to reveal)

### Add Twilio Credential in n8n:

1. In n8n → **Settings** → **Credentials**
2. Click **"Add Credential"**
3. Search for **"Twilio API"**
4. Enter:
   - Account SID: [paste from Twilio]
   - Auth Token: [paste from Twilio]
5. Name it: `Twilio SMS`
6. Click **"Save"**

### Import SMS Workflow:

1. Import: `3-sms-followup-automation.json`
2. Update Google Sheets credential
3. Update Twilio credential
4. In the "Send SMS" node, change the **From** number to your Twilio number
5. Test and activate

---

## STEP 8: Set Up High-Value Lead Alerts (5 minutes)

1. Import: `4-high-value-lead-alert.json`
2. Update all credentials
3. In the SMS node, change the phone number to YOUR personal cell
4. In the Email node, change the recipient to YOUR email
5. Test with a high-value test lead (Estimated Value > $500,000)
6. Activate

---

## STEP 9: Activate AI Chatbot on Website (5 minutes)

The chatbot code already exists. To activate:

1. Open `/Users/jumaanebey/Documents/stop-foreclosure-fast/index.html`
2. The chat widget code is already in the file (currently has CSP issues)
3. For a quick solution, we can add a simple chat trigger that opens SMS

I'll add this for you now if you confirm.

---

## STEP 10: Set Up ConvertKit (Optional - 15 minutes)

ConvertKit is for email marketing sequences.

### Create Account:

1. Go to https://convertkit.com
2. Sign up (free for first 1,000 subscribers)
3. Confirm your email

### Create a Form:

1. In ConvertKit, go to **Grow** → **Landing Pages & Forms**
2. Click **"Create New"** → **"Form"**
3. Choose **"Inline"** form type
4. Name it: "Foreclosure Consultation"
5. Add fields: Name, Email, Phone
6. Click **"Save"**

### Get Form ID:

1. Click on your form
2. Go to **Embed**
3. Copy the form ID from the embed code (looks like: `data-form="1234567"`)

### Connect to n8n:

1. In n8n → **Settings** → **Credentials**
2. Add **"ConvertKit API"** credential
3. Get API key from ConvertKit: **Settings** → **Advanced** → **API**
4. Paste API key in n8n

---

## Checklist Summary

### Must Do (Core Automation):
- [ ] Create n8n account
- [ ] Connect Google Sheets credential
- [ ] Set up Gmail SMTP credential
- [ ] Create lead tracking Google Sheet
- [ ] Import & activate email follow-up workflow
- [ ] Import & activate daily report workflow
- [ ] Test with 1-2 test leads

### Optional (Enhanced):
- [ ] Set up Twilio for SMS ($11/month)
- [ ] Import SMS follow-up workflow
- [ ] Import high-value lead alert workflow
- [ ] Set up ConvertKit for email marketing

---

## Troubleshooting

### "Google Sheets not connecting"
- Re-authenticate the credential
- Make sure Sheet ID is correct (no extra spaces)
- Sheet tab name must match exactly

### "Emails not sending"
- Use App Password, not your regular Gmail password
- Enable 2-Step Verification first
- Check spam folder

### "Workflow not running"
- Make sure "Active" toggle is ON (green)
- Check n8n execution logs for errors
- Verify schedule trigger timezone

### "SMS not sending"
- Twilio number must include country code (+1)
- Check Twilio account balance
- Verify the phone number is SMS-capable

---

## Monthly Costs

| Service | Cost |
|---------|------|
| n8n Cloud (Free tier) | $0 |
| Gmail SMTP | $0 |
| Google Sheets | $0 |
| Twilio (optional) | ~$11/month |
| ConvertKit (optional) | $0 (free tier) |
| **Total (basic)** | **$0/month** |
| **Total (with SMS)** | **~$11/month** |

---

## Questions?

If you get stuck on any step, tell me:
1. Which step number
2. What error you're seeing
3. Screenshot if possible

I'll help you troubleshoot.

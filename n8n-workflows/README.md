# n8n Workflows for Foreclosure Lead Automation

## Overview

These 4 n8n workflows automate your entire foreclosure lead process - from initial outreach to follow-up to high-value lead alerts.

## Workflows Included

### 1. Email Follow-up Automation
**File:** `1-email-followup-automation.json`

**What it does:**
- Checks Google Sheet every 15 minutes for new leads
- Automatically sends personalized email to leads with status "New"
- Updates status to "Email Sent" with timestamp
- Tracks last contact date

**Requirements:**
- Google Sheets OAuth2 credentials
- SMTP credentials (Gmail, SendGrid, etc.)

---

### 2. Daily Lead Report
**File:** `2-daily-lead-report.json`

**What it does:**
- Runs every morning at 8 AM
- Calculates stats: new leads, follow-ups needed, appointments today
- Sends you a formatted email summary
- Includes actionable lead lists

**Requirements:**
- Google Sheets OAuth2 credentials
- SMTP credentials

**Sample Report:**
```
📊 DAILY SUMMARY

🆕 New Leads Yesterday: 12
📞 Follow-ups Needed Today: 8
📅 Appointments Today: 3

📈 Overall Stats:
   • Total Leads in Pipeline: 247
   • Contacted: 89
   • Contact Rate: 36%
```

---

### 3. SMS Follow-up Automation
**File:** `3-sms-followup-automation.json`

**What it does:**
- Runs every 6 hours
- Finds leads with status "Email Sent" and phone number
- Waits 48 hours after email
- Sends SMS follow-up via Twilio
- Updates status to "SMS Sent"

**Requirements:**
- Google Sheets OAuth2 credentials
- Twilio account + phone number (~$1/month + $0.0079/SMS)

**SMS Template:**
```
Hi [Name], this is [YOUR NAME] with My Foreclosure Solution.
I sent you an email about [Address]. I help CA homeowners
stop foreclosure. Free consultation: (949) 328-4811.
Text STOP to opt out.
```

**Cost:** ~$8-16/month for 1,000-2,000 SMS

---

### 4. High-Value Lead Alert
**File:** `4-high-value-lead-alert.json`

**What it does:**
- Triggers when new row is added to Google Sheet
- Calculates estimated equity
- If equity > $100,000 OR property value > $500,000:
  - Sends you instant SMS alert
  - Sends detailed HTML email with lead analysis
  - Tags lead in Google Sheet as "HIGH-VALUE"

**Requirements:**
- Google Sheets OAuth2 credentials
- Twilio account (for SMS alerts)
- SMTP credentials (for email)

**Why This Matters:**
High-equity leads = bigger commissions. This ensures you never miss a $20k+ deal.

---

## Setup Instructions

### Step 1: Install n8n

**Option A: n8n Cloud (Easiest)**
1. Go to https://n8n.io/cloud/
2. Sign up (free tier: 2,500 executions/month)
3. Skip to Step 2

**Option B: Self-Hosted (Free Forever)**
```bash
# Using Docker (recommended)
docker volume create n8n_data
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n

# Access at http://localhost:5678
```

### Step 2: Set Up Credentials

**A. Google Sheets OAuth2:**
1. In n8n, go to Settings → Credentials
2. Click "Add Credential" → "Google Sheets API"
3. Choose "OAuth2"
4. Follow the setup wizard to connect your Google account
5. Grant access to Google Sheets

**B. SMTP (Gmail):**
1. In n8n, go to Settings → Credentials
2. Click "Add Credential" → "SMTP"
3. Enter details:
   ```
   Host: smtp.gmail.com
   Port: 587
   Security: TLS
   User: help@myforeclosuresolution.com
   Password: [App Password - see below]
   ```

**To get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Copy the 16-character password
4. Use this instead of your regular password

**C. Twilio (Optional - for SMS workflows):**
1. Sign up at https://www.twilio.com/
2. Get a phone number ($1/month)
3. In n8n, add Twilio credentials:
   - Account SID (from Twilio dashboard)
   - Auth Token (from Twilio dashboard)

### Step 3: Import Workflows

1. In n8n, click "Add Workflow"
2. Click the menu (⋮) → "Import from File"
3. Select the workflow JSON file
4. Click "Import"

**Start with these two:**
- `1-email-followup-automation.json`
- `2-daily-lead-report.json`

### Step 4: Configure Each Workflow

After importing, you need to update placeholders:

**In Workflow 1 (Email Follow-up):**
1. Open the "Get New Leads from Sheet" node
2. Select your Google Sheets credential
3. Document ID should already be: `1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw`
4. Open the "Send Initial Email" node
5. Replace `[YOUR NAME]` with your actual name
6. Select your SMTP credential
7. Test the workflow with "Execute Workflow" button

**In Workflow 2 (Daily Report):**
1. Update Google Sheets credential
2. Update SMTP credential
3. Test execution

**In Workflow 3 (SMS Follow-up):**
1. Update all credentials
2. Replace `+1YOUR_TWILIO_NUMBER` with your Twilio number
3. Replace `[YOUR NAME]` in SMS text
4. Test with one lead first

**In Workflow 4 (High-Value Alert):**
1. Update all credentials
2. Replace `+19493284811` with your personal phone number
3. Test with a high-value lead

### Step 5: Activate Workflows

1. Click the "Active" toggle in the top-right of each workflow
2. Workflows will now run automatically

---

## Testing Your Workflows

### Test Workflow 1 (Email Follow-up):
1. Add a test lead to your Google Sheet:
   ```
   Name: Test User
   Email: your-email@gmail.com
   Property Address: 123 Test St, LA, CA
   Status: New
   ```
2. Wait 15 minutes (or click "Execute Workflow" to run immediately)
3. Check your email
4. Verify Google Sheet status updated to "Email Sent"

### Test Workflow 2 (Daily Report):
1. Click "Execute Workflow" to run immediately (don't wait until 8 AM)
2. Check your email for the daily summary
3. Verify stats are accurate

### Test Workflow 3 (SMS):
1. Manually set a lead's status to "Email Sent - [2 days ago date]"
2. Add your phone number to that lead
3. Run workflow manually
4. Check if you receive SMS

### Test Workflow 4 (High-Value):
1. Add a test lead with:
   ```
   Estimated Value: 600000
   Owner Name: High Value Test
   ```
2. You should receive SMS + email alert immediately

---

## Monitoring & Troubleshooting

### Check Execution Logs:
1. Go to "Executions" tab in n8n
2. See history of all workflow runs
3. Green = success, Red = error
4. Click any execution to see detailed logs

### Common Issues:

**"Could not connect to Google Sheets"**
- Re-authenticate your Google OAuth2 credential
- Make sure sheet ID is correct
- Verify sheet tab name is "NOD Leads"

**"Email not sending"**
- Check SMTP credentials
- Use Gmail App Password (not regular password)
- Verify Gmail allows "Less secure apps" or use App Password

**"SMS not sending"**
- Verify Twilio phone number is correct (include +1)
- Check Twilio account balance
- Make sure phone number includes country code

**"Workflow not triggering"**
- Make sure workflow is "Active" (toggle in top-right)
- Check schedule settings (time zones!)
- View execution logs for errors

---

## Execution Limits

### n8n Cloud Free Tier:
- 2,500 executions/month
- Good for ~50-100 leads/month

**Example:**
- Email follow-up: 4 checks/hour × 24 hours × 30 days = 2,880/month ❌ (too many)
- Solution: Change to "Every 30 minutes" = 1,440/month ✅

### n8n Cloud Starter ($20/month):
- 20,000 executions/month
- Good for 500+ leads/month

### Self-Hosted:
- Unlimited executions
- Free forever
- Requires server/computer to run 24/7

---

## Optimization Tips

### Reduce Execution Count:

**Workflow 1 (Email):**
- Change from "Every 15 min" → "Every 30 min" or "Every 1 hour"
- Still fast enough for lead response

**Workflow 3 (SMS):**
- Change from "Every 6 hours" → "Every 12 hours"
- 48-hour delay is still effective

### Use Webhooks Instead of Polling:

For instant triggers (advanced):
1. Use Google Sheets Trigger node (webhook-based)
2. Only executes when row is actually added
3. Saves executions vs. polling every X minutes

---

## Advanced Customization

### Customize Email Templates:
Edit the "message" field in "Send Initial Email" node with your own copy.

### Add More Filters:
Add additional "IF" nodes to filter by:
- County (only LA County)
- Days Since NOD (only urgent leads)
- Property value (only high-value)

### Add More Actions:
After sending email, you can:
- Add to Airtable CRM
- Create task in Monday.com
- Post to Slack channel
- Add to Mailchimp list

### Drip Campaign Sequence:

Create multiple workflows:
```
Day 0: New lead → Send initial email
Day 2: No response → Send follow-up email
Day 3: No response → Send SMS
Day 7: No response → Send value email
Day 14: No response → Final outreach
```

Each workflow filters by "Last Contact" date and status.

---

## Cost Summary

**Free Option:**
- n8n: Self-hosted (free)
- Google Sheets: Free
- Gmail SMTP: Free
- Total: $0/month

**Recommended Setup:**
- n8n Cloud Starter: $20/month
- Twilio: $1/month + $0.0079/SMS (~$10/month for 1,000 SMS)
- Total: ~$30/month

**ROI:**
- 1 deal = $5,000-18,000
- Automation cost: $30/month
- ROI: 166x - 600x

---

## Support

**n8n Community:**
- Forum: https://community.n8n.io/
- Documentation: https://docs.n8n.io/

**Workflow Issues:**
- Check execution logs
- Verify all credentials are connected
- Test each node individually

**Questions?**
Open an issue in your GitHub repo or reference the N8N-AUTOMATION-GUIDE.md for more details.

---

## Next Steps

1. ✅ Install n8n (cloud or self-hosted)
2. ✅ Set up Google Sheets + SMTP credentials
3. ✅ Import Workflow 1 & 2
4. ✅ Test with 1-2 leads
5. ✅ Activate workflows
6. ✅ Monitor for 1 week
7. ✅ Add Workflow 3 & 4 when comfortable
8. ✅ Scale to 100+ leads/month

**You're now ready to automate your foreclosure lead business!** 🚀

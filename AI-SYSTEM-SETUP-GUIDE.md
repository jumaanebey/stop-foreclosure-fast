# AI Agent System - Complete Setup Guide

## Overview

This guide will help you deploy your complete AI agent system for automated foreclosure lead management.

**What You're Building:**
- AI Chatbot on website (24/7 lead capture)
- AI Lead Scorer (prioritizes hot leads)
- AI Email Responder (auto-replies to leads)
- AI Voice Agent (calls high-priority leads)
- Follow-up Automation (30-day nurture sequence)

**Time to Deploy:** 2-4 hours
**Cost:** ~$25-950/month (depending on which features you activate)

---

## 🎯 What Was Built For You

### ✅ Files Created:

1. **ai-chatbot.html** - Custom AI chatbot (OpenAI-powered)
2. **CHATBOT-EMBED-CODE.md** - Instructions to add chatbot to website
3. **n8n-workflows/1-chatbot-to-sheets.json** - Chatbot → Google Sheets
4. **n8n-workflows/2-ai-email-responder.json** - Auto-reply to emails
5. **n8n-workflows/3-ai-voice-agent.json** - Bland AI call automation
6. **n8n-workflows/4-follow-up-automation.json** - 30-day drip campaign
7. **n8n-workflows/5-ai-lead-scorer.json** - AI lead prioritization (already exists)
8. **AI-SYSTEM-SETUP-GUIDE.md** - This file

---

## 📋 Prerequisites (What You Need)

### Accounts & Services:

| Service | Purpose | Cost | Required? |
|---------|---------|------|-----------|
| **OpenAI** | AI chatbot & email responses | ~$3-10/mo | ✅ YES |
| **n8n** | Automation platform | $0 (self-host) or $20/mo (cloud) | ✅ YES |
| **Google Sheets** | Lead storage | Free | ✅ YES |
| **Gmail** | Email automation | Free | ✅ YES |
| **Bland AI** | Voice agent calls | ~$900/mo for 100 calls/day | ⚠️ OPTIONAL |
| **Your website** | Chatbot hosting | Already have | ✅ YES |

### API Keys Needed:
- [ ] OpenAI API key
- [ ] Google Sheets OAuth credentials
- [ ] Gmail OAuth credentials
- [ ] Bland AI API key (optional)

---

## 🚀 Deployment Plan

### Phase 1: Quick Start (1 hour) - FREE
**Cost: ~$3/month**

1. ✅ Set up AI Chatbot on website
2. ✅ Import "Chatbot to Google Sheets" workflow
3. ✅ Import "AI Lead Scorer" workflow

**Result:** Chatbot captures leads → Saves to sheet → AI scores them

### Phase 2: Email Automation (30 minutes) - FREE
**Cost: +$0/month**

4. ✅ Import "AI Email Responder" workflow
5. ✅ Import "Follow-up Automation" workflow

**Result:** Auto-reply to lead emails + 30-day nurture sequence

### Phase 3: Voice Agent (1 hour) - PAID
**Cost: +$900/month**

6. ✅ Sign up for Bland AI
7. ✅ Import "AI Voice Agent" workflow

**Result:** AI calls high-priority leads automatically

---

## 📝 Step-by-Step Setup

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Add billing info (you'll spend ~$3-10/month)

**Save this key** - you'll need it for:
- Chatbot configuration
- n8n workflows

---

### Step 2: Set Up Google Sheet

1. Open this Google Sheet (or create new one):
   - URL: https://docs.google.com/spreadsheets/d/1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw/edit

2. Create these columns (if not already there):
   ```
   | Timestamp | Owner Name | Phone Number | Email | Property Address |
   | County | Lender | Recording Date | Days Since NOD | Estimated Value |
   | Priority Score | Status | Call Status | Last Contact | Notes |
   | Conversation Summary | Source |
   ```

3. Name the sheet tab: **"NOD Leads"**

4. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS-IS-THE-SHEET-ID]/edit
   ```

---

### Step 3: Deploy AI Chatbot to Website

#### Option A: Quick Embed (Recommended)

1. Open `ai-chatbot.html`

2. Update configuration (lines 251-252):
   ```javascript
   OPENAI_API_KEY: 'sk-YOUR-KEY-HERE',  // Your OpenAI key from Step 1
   GOOGLE_SHEET_WEBHOOK: 'https://your-n8n-url/webhook/chatbot-lead'  // Will get this in Step 4
   ```

3. Upload `ai-chatbot.html` to your website hosting

4. Add this code before `</body>` tag on EVERY page:
   ```html
   <script src="https://yourdomain.com/ai-chatbot.html"></script>
   ```

#### Option B: Direct Embed

Copy the entire contents of `ai-chatbot.html` and paste before `</body>` on each page.

**Test It:**
1. Visit your website
2. Click chatbot button (bottom right)
3. Type: "I received a foreclosure notice"
4. Complete the conversation

---

### Step 4: Import n8n Workflows

#### A. Set Up n8n (if you haven't)

**Option 1: n8n Cloud (Easiest)**
1. Go to https://n8n.io/pricing
2. Sign up for free trial or $20/month plan
3. Skip to "B. Import Workflows"

**Option 2: Self-Host (Free)**
```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Then open: http://localhost:5678

#### B. Import Workflows

For EACH workflow file:

1. In n8n, click **"+"** → **"Import from File"**

2. Import in this order:
   - ✅ `n8n-workflows/1-chatbot-to-sheets.json`
   - ✅ `n8n-workflows/5-ai-lead-scorer.json` (already exists)
   - ✅ `n8n-workflows/2-ai-email-responder.json`
   - ✅ `n8n-workflows/4-follow-up-automation.json`
   - ⚠️ `n8n-workflows/3-ai-voice-agent.json` (requires Bland AI)

3. For each workflow, click to edit it

---

### Step 5: Configure Workflow #1 - Chatbot to Google Sheets

1. Open workflow: **"Chatbot to Google Sheets - Lead Capture"**

2. **Webhook Node** (first node):
   - Click to open
   - Copy the webhook URL (looks like: `https://your-n8n.com/webhook/chatbot-lead`)
   - Save this URL

3. **Add to Google Sheet Node**:
   - Click "Add to Google Sheet" node
   - Click "Credential to connect with"
   - Add Google Sheets OAuth2 credential
   - Authenticate with your Google account
   - Select your spreadsheet (paste Sheet ID from Step 2)
   - Select sheet name: "NOD Leads"

4. **Send Notification Email Node**:
   - Update "fromEmail" and "toEmail" to your email
   - Or connect your email service (Gmail, SendGrid, etc.)

5. **Update chatbot with webhook URL**:
   - Go back to `ai-chatbot.html`
   - Update line 252:
     ```javascript
     GOOGLE_SHEET_WEBHOOK: 'YOUR-WEBHOOK-URL-FROM-STEP-2'
     ```
   - Re-upload to your website

6. **Activate workflow** (toggle switch at top)

**Test It:**
- Go to your website
- Use chatbot to submit a lead
- Check if lead appears in Google Sheet
- Check if you got notification email

---

### Step 6: Configure Workflow #2 - AI Lead Scorer

1. Open workflow: **"AI Lead Scorer - OpenAI Priority Analysis"**

2. **OpenAI Node**:
   - Click "OpenAI - Score Lead" node
   - Add OpenAI API credential
   - Paste your OpenAI API key
   - Save

3. **Update Sheet Nodes**:
   - For both Google Sheets nodes, authenticate with same Google account
   - Select same spreadsheet
   - Select sheet: "NOD Leads"

4. **Customize scoring** (optional):
   - Edit the system prompt in OpenAI node to adjust scoring criteria

5. **Activate workflow**

**Test It:**
- Add a new lead to your sheet (or use chatbot)
- Wait 5 minutes
- Check if "Priority Score" column gets filled
- Check if you receive high-priority alert email (for score >= 7)

---

### Step 7: Configure Workflow #3 - AI Email Responder

1. Open workflow: **"AI Email Responder - Auto-Reply to Leads"**

2. **Gmail Trigger Node**:
   - Click "When Email Received"
   - Add Gmail OAuth2 credential
   - Authenticate with your Gmail account
   - Set to check inbox every 5 minutes

3. **Lookup Lead Node**:
   - Add Google Sheets credential
   - Select your spreadsheet
   - Select sheet: "NOD Leads"

4. **OpenAI Node**:
   - Add your OpenAI API credential
   - Customize the email response prompts if desired

5. **Send Email Reply Node**:
   - Add Gmail credential
   - Test with a sample email

6. **Update Lead Sheet Node**:
   - Connect Google Sheets credential

7. **Activate workflow**

**Test It:**
- Add a lead to your sheet with email address
- Send email from that address to your Gmail
- Wait 5 minutes
- Check if you receive AI-generated response
- Check if you got notification of AI response

---

### Step 8: Configure Workflow #4 - Follow-up Automation

1. Open workflow: **"Follow-up Automation - 30-Day Drip Campaign"**

2. **Schedule Trigger**:
   - Already set to run daily at 9 AM
   - Adjust time if desired (click node → change cron expression)

3. **Get All Leads Node**:
   - Add Google Sheets credential
   - Select spreadsheet & sheet

4. **OpenAI Node**:
   - Add OpenAI credential

5. **Send Email Node**:
   - Configure your email service
   - Update "fromEmail" to your email

6. **Update Sheet Node**:
   - Add Google Sheets credential

7. **Activate workflow**

**How It Works:**
- Checks leads daily at 9 AM
- Finds leads needing follow-up based on days since last contact
- Generates personalized email with GPT-4
- Sends follow-up emails automatically:
  - Day 2: Check-in
  - Day 7: Value/education
  - Day 14: Case study
  - Day 21: Urgency
  - Day 30: Final follow-up

---

### Step 9: Configure Workflow #5 - AI Voice Agent (Optional - Requires Bland AI)

⚠️ **This workflow costs ~$900/month for 100 calls/day**

Only proceed if you want AI to make phone calls automatically.

#### A. Sign Up for Bland AI

1. Go to https://www.bland.ai/
2. Sign up for account
3. Add credits ($50 minimum)
4. Go to Settings → API Keys
5. Copy your API key

#### B. Configure Workflow

1. Open workflow: **"AI Voice Agent - Bland AI Call Automation"**

2. **Bland AI Call Node**:
   - Click "Bland AI - Make Call" node
   - Find the authorization header parameter
   - Replace `YOUR_BLAND_AI_API_KEY` with your key

3. **Customize call script** (optional):
   - Edit the "prompt" parameter to adjust Sarah's personality
   - Modify qualifying questions
   - Change appointment availability

4. **Update webhook callback**:
   - Find "Webhook - Call Completed" node
   - Copy webhook URL
   - In "Bland AI - Make Call" node, update webhook parameter

5. **Configure Google Sheets nodes** (2 of them)

6. **Activate workflow**

**How It Works:**
- Monitors Google Sheet for new high-priority leads (score >= 7)
- Checks if lead has phone number and hasn't been called
- Sends call request to Bland AI
- Sarah (AI voice agent) calls the lead
- Has empathetic conversation and tries to book appointment
- Receives callback when call completes
- Updates sheet with results, transcript, recording
- Notifies you via email

**Test It:**
- Add a test lead with Priority Score = 8 and your phone number
- Wait ~5 minutes
- You should receive a call from Sarah
- After call, check sheet for results and recording

---

## 💰 Cost Breakdown

### Phase 1 (Basic - Chatbot + Scoring)
- OpenAI API: $3-10/month
- n8n: Free (self-host) or $20/month (cloud)
- **Total: $3-30/month**

### Phase 2 (Add Email Automation)
- Same as Phase 1 (email responses use OpenAI)
- **Total: $3-30/month**

### Phase 3 (Add Voice Agent)
- Bland AI: $900/month (100 calls/day at $0.09/min × 5 min avg)
- **Total: $903-930/month**

### ROI Calculation:

**If AI Voice Agent books 10 appointments/month:**
- 2 deals close = $10,000-$36,000 revenue
- Cost: $930
- **ROI: 11x-40x**

---

## 🧪 Testing Your System

### End-to-End Test:

1. **Test Chatbot:**
   - Visit website
   - Use chatbot
   - Submit lead info
   - Verify appears in Google Sheet

2. **Test Lead Scorer:**
   - Wait 5 minutes after lead added
   - Check if Priority Score filled in
   - Check if you got alert (if high priority)

3. **Test Email Responder:**
   - Email your Gmail from the lead's email
   - Wait 5 minutes
   - Verify you got AI response

4. **Test Follow-up:**
   - Wait until 9 AM next day
   - Check if follow-up emails sent to Day 2, 7, 14, 21, or 30 leads

5. **Test Voice Agent** (if activated):
   - Add test lead with Priority Score = 8
   - Add your phone number
   - Wait 5 minutes
   - Receive call from Sarah

---

## 🎨 Customization Options

### Chatbot Customization:

**Change Colors** (`ai-chatbot.html` lines 32-33):
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change to your brand colors */
```

**Change Name** (line 236):
```html
<h3>Foreclosure Helper</h3>
<!-- Change to your preferred name -->
```

**Adjust AI Personality** (lines 253-289):
```javascript
SYSTEM_PROMPT: `You are a helpful, empathetic AI assistant...`
/* Modify tone, style, and conversation flow */
```

### Workflow Customization:

**Lead Scorer - Adjust Scoring Criteria:**
- Edit OpenAI system prompt in workflow #2
- Change point values for equity, property value, etc.

**Email Responder - Adjust Response Style:**
- Edit OpenAI system prompt in workflow #3
- Change tone, length, CTA style

**Voice Agent - Adjust Call Script:**
- Edit Bland AI prompt in workflow #5
- Change Sarah's personality
- Modify qualifying questions
- Adjust appointment times

**Follow-up - Adjust Schedule:**
- Edit JavaScript code in workflow #4
- Change follow-up days (currently 2, 7, 14, 21, 30)
- Add/remove email types

---

## 🔧 Troubleshooting

### Chatbot doesn't appear on website:
- Check if script is loaded (view page source)
- Check browser console for errors (F12 → Console)
- Verify `ai-chatbot.html` is accessible at the URL

### Chatbot doesn't respond:
- Verify OpenAI API key is correct
- Check API key has billing enabled and credits
- Check browser console for API errors

### Leads not saving to Google Sheet:
- Verify n8n workflow is active
- Check webhook URL in chatbot config matches n8n
- Test webhook URL with curl or Postman
- Check n8n execution log for errors

### AI Lead Scorer not scoring leads:
- Verify workflow is active
- Check OpenAI credentials are configured
- Check Google Sheets is connected
- Manually trigger workflow to test

### Email Responder not replying:
- Verify Gmail OAuth is connected and working
- Check if lead's email exists in sheet
- Check OpenAI API is working
- Review n8n execution logs

### Voice Agent not calling:
- Verify Bland AI API key is correct
- Check Bland AI account has credits
- Verify webhook URL is accessible from internet (not localhost)
- Check n8n execution logs

---

## 📊 Monitoring & Analytics

### What to Track:

1. **Lead Volume:**
   - Chatbot conversations per day
   - Leads captured per day

2. **Lead Quality:**
   - Average priority score
   - % high-priority leads (score >= 7)

3. **Engagement:**
   - Email response rate
   - Call pickup rate (if using voice agent)
   - Appointment booking rate

4. **Conversion:**
   - Leads → Appointments
   - Appointments → Deals
   - Revenue per lead

### n8n Execution Dashboard:

- View executions: n8n Dashboard → Executions
- Filter by workflow
- Check success/failure rate
- Review error logs

---

## 🔐 Security & Privacy

### Best Practices:

1. **API Keys:**
   - Never commit API keys to GitHub
   - Store in environment variables or n8n credentials
   - Rotate keys periodically

2. **Webhook URLs:**
   - Use HTTPS only
   - Consider adding authentication
   - Rate limit to prevent abuse

3. **Lead Data:**
   - Comply with GDPR/CCPA if applicable
   - Secure Google Sheet (don't make public)
   - Regular backups of lead data

4. **Email Content:**
   - Review AI responses periodically
   - Add disclaimers where appropriate
   - Monitor for inappropriate content

---

## 📈 Optimization Tips

### Week 1-2: Monitor and Adjust

1. **Review all AI responses:**
   - Email responses - are they helpful?
   - Voice agent calls - is Sarah effective?
   - Chatbot conversations - is it capturing leads?

2. **Adjust prompts:**
   - Make AI more/less formal
   - Change conversation flow
   - Update qualifying questions

3. **Track metrics:**
   - Lead capture rate
   - Response rates
   - Booking rates

### Week 3-4: Scale and Improve

1. **Add more workflows:**
   - SMS notifications for high-priority leads
   - Slack/Discord alerts
   - Calendar integrations

2. **Improve lead quality:**
   - Adjust chatbot qualification questions
   - Update lead scoring criteria
   - Add skip tracing for missing phone numbers

3. **A/B test:**
   - Different chatbot greetings
   - Different email subject lines
   - Different call scripts

---

## 🆘 Support & Resources

### Documentation:
- n8n Docs: https://docs.n8n.io/
- OpenAI API Docs: https://platform.openai.com/docs
- Bland AI Docs: https://docs.bland.ai/

### Community:
- n8n Community: https://community.n8n.io/
- OpenAI Community: https://community.openai.com/

### Your Files:
- **AI-AGENT-SYSTEM.md** - Strategy and architecture overview
- **CHATBOT-EMBED-CODE.md** - Chatbot setup instructions
- **AI-SYSTEM-SETUP-GUIDE.md** - This file
- **n8n-workflows/** - All workflow JSON files

---

## ✅ Launch Checklist

Before going live:

- [ ] OpenAI API key configured and billing enabled
- [ ] Google Sheet created with correct columns
- [ ] Chatbot embedded on all website pages
- [ ] Chatbot tested end-to-end
- [ ] Workflow #1 (Chatbot → Sheets) active and tested
- [ ] Workflow #2 (Lead Scorer) active and tested
- [ ] Workflow #3 (Email Responder) active and tested
- [ ] Workflow #4 (Follow-up) active and tested
- [ ] Workflow #5 (Voice Agent) configured if using Bland AI
- [ ] All email notifications going to correct address
- [ ] Test lead submitted and processed successfully
- [ ] Monitored first 10-20 leads for issues
- [ ] Reviewed AI responses for quality
- [ ] Backups of Google Sheet set up

---

## 🎉 You're Done!

Your AI agent system is now:
- ✅ Capturing leads 24/7 via chatbot
- ✅ Scoring and prioritizing leads automatically
- ✅ Responding to emails instantly
- ✅ Following up for 30 days
- ✅ (Optional) Calling high-priority leads

**Next Steps:**
1. Monitor for first week
2. Adjust prompts based on results
3. Track conversions
4. Scale up (add voice agent if not using)
5. Celebrate your automation!

**Your job now:**
- Show up to appointments
- Close deals
- Collect commissions

The AI handles everything else! 🚀

---

**Questions?** Review the documentation files or check n8n execution logs for errors.

**Ready to scale?** Consider adding:
- SMS notifications (Twilio)
- CRM integration (HubSpot, Salesforce)
- Calendar booking (Calendly)
- Additional AI agents for different scenarios

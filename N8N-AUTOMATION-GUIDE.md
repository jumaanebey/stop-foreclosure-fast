# n8n Automation Guide - Foreclosure Lead System

## What n8n Can Automate For You

n8n is a powerful workflow automation tool that can handle repetitive tasks in your foreclosure business. Here's what we can automate:

### 1. **Automatic Email Follow-ups**
- Send personalized emails based on lead status
- Automatic drip campaigns
- Follow-up reminders
- Appointment confirmations

### 2. **Lead Data Enrichment**
- Auto-lookup phone numbers (skip tracing)
- Pull property values from Zillow API
- Get homeowner contact info
- Calculate equity automatically

### 3. **Google Sheet Automation**
- Auto-update lead status
- Set follow-up reminders
- Track days since NOD
- Alert on high-value leads

### 4. **SMS/Text Message Automation**
- Send initial outreach via text
- Appointment reminders
- Follow-up sequences
- Emergency alerts for urgent leads

### 5. **CRM Integration**
- Sync with Airtable, Notion, or Monday.com
- Auto-create tasks for each new lead
- Pipeline management
- Deal tracking

---

## n8n Setup (Quick Start)

### Option 1: Self-Hosted (Free Forever)

**Install via Docker (Recommended):**

```bash
# Install n8n with Docker
docker volume create n8n_data
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

**Access:** http://localhost:5678

### Option 2: n8n Cloud (Easiest)

1. Go to https://n8n.io/cloud/
2. Sign up for free tier (2,500 executions/month)
3. Access your instance immediately

---

## Workflow 1: Automatic Email Follow-up System

**What it does:** Automatically sends personalized follow-up emails based on lead status in Google Sheets.

### Workflow Diagram:
```
Google Sheets (Trigger)
→ Filter (Status = "New")
→ Email (Send template)
→ Update Sheet (Status = "Email Sent")
```

### n8n Workflow JSON:

{% raw %}
```json
{
  "name": "Foreclosure Lead Email Follow-up",
  "nodes": [
    {
      "parameters": {
        "pollTimes": {
          "item": [
            {
              "mode": "everyMinute",
              "minute": 15
            }
          ]
        },
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!A:N"
      },
      "name": "Google Sheets - Get New Leads",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json['Status']}}",
              "operation": "equals",
              "value2": "New"
            }
          ]
        }
      },
      "name": "Filter - Only New Leads",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "fromEmail": "help@myforeclosuresolution.com",
        "toEmail": "={{$json['Email']}}",
        "subject": "Important information about {{$json['Property Address']}}",
        "text": "Hi {{$json['Owner Name']}},\n\nMy name is [YOUR NAME], and I'm a licensed California real estate professional specializing in foreclosure assistance.\n\nI noticed you received a Notice of Default on your property at {{$json['Property Address']}}. I'm reaching out because I've helped over 500 California homeowners in similar situations.\n\nYou still have options to stop the foreclosure or sell with equity intact.\n\nI'm offering a free consultation. Call me at (949) 565-5285.\n\nBest regards,\n[YOUR NAME]\nMy Foreclosure Solution\nCA DRE #02076038"
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!K{{$json['row']}}",
        "options": {
          "valueInputMode": "USER_ENTERED"
        },
        "dataToSend": "autoMap",
        "values": {
          "Status": "Email Sent - {{$now.format('MM/DD/YYYY')}}"
        }
      },
      "name": "Update Google Sheet Status",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [850, 300]
    }
  ],
  "connections": {
    "Google Sheets - Get New Leads": {
      "main": [[{"node": "Filter - Only New Leads", "type": "main", "index": 0}]]
    },
    "Filter - Only New Leads": {
      "main": [[{"node": "Send Email", "type": "main", "index": 0}]]
    },
    "Send Email": {
      "main": [[{"node": "Update Google Sheet Status", "type": "main", "index": 0}]]
    }
  }
}
```
{% endraw %}

**How to Import:**
1. Open n8n
2. Click "Add workflow" → "Import from File"
3. Paste the JSON above
4. Configure your Google Sheets credentials
5. Activate workflow

---

## Workflow 2: Skip Tracing Automation (Phone Number Lookup)

**What it does:** Automatically looks up phone numbers for leads missing contact info.

### Required Services:
- **BeenVerified API** ($25/month unlimited)
- **TruePeopleSearch** (free but rate-limited)
- **BatchSkipTracing API** ($0.15/lookup)

### Workflow:

```
Google Sheets Trigger (New row added)
→ Check if phone number exists
→ If NO → Call Skip Tracing API
→ Update sheet with phone number
→ Send you a notification
```

### n8n Workflow JSON:

{% raw %}
```json
{
  "name": "Auto Skip Trace New Leads",
  "nodes": [
    {
      "parameters": {
        "triggerOn": "specificSheet",
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "event": "row.create"
      },
      "name": "Google Sheets - New Row Trigger",
      "type": "n8n-nodes-base.googleSheetsTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json['Phone Number']}}",
              "operation": "isEmpty"
            }
          ]
        }
      },
      "name": "Check if Phone Missing",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "https://api.batchskiptracing.com/v1/lookup",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Authorization",
              "value": "Bearer YOUR_API_KEY"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "address",
              "value": "={{$json['Property Address']}}"
            },
            {
              "name": "name",
              "value": "={{$json['Owner Name']}}"
            }
          ]
        }
      },
      "name": "Skip Trace API Call",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [650, 300]
    },
    {
      "parameters": {
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!D{{$json['row']}}",
        "dataToSend": "autoMap",
        "values": {
          "Phone Number": "={{$json['phone']}}"
        }
      },
      "name": "Update Sheet with Phone",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [850, 300]
    }
  ]
}
```
{% endraw %}

---

## Workflow 3: Daily Lead Report Email

**What it does:** Sends you a summary email every morning with new leads and follow-ups needed.

### Workflow:

```
Schedule Trigger (Daily at 8 AM)
→ Get Google Sheets data
→ Filter new leads from yesterday
→ Count appointments today
→ Format email with summary
→ Send to your email
```

### n8n Workflow JSON:

{% raw %}
```json
{
  "name": "Daily Lead Report",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtHour": 8
            }
          ]
        }
      },
      "name": "Schedule - Daily 8 AM",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!A:N"
      },
      "name": "Get All Leads",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [450, 300]
    },
    {
      "parameters": {
        "jsCode": "const today = new Date().toISOString().split('T')[0];\nconst yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];\n\nconst newLeads = items.filter(item => item.json['Date Found'] === yesterday);\nconst followupsToday = items.filter(item => item.json['Next Follow-up Date'] === today);\nconst appointmentsToday = items.filter(item => \n  item.json['Status'].includes('Appointment') && \n  item.json['Next Follow-up Date'] === today\n);\n\nreturn [\n  {\n    json: {\n      newLeadsCount: newLeads.length,\n      followupsCount: followupsToday.length,\n      appointmentsCount: appointmentsToday.length,\n      newLeads: newLeads,\n      followups: followupsToday,\n      appointments: appointmentsToday\n    }\n  }\n];"
      },
      "name": "Calculate Stats",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "fromEmail": "help@myforeclosuresolution.com",
        "toEmail": "help@myforeclosuresolution.com",
        "subject": "Daily Lead Report - {{$now.format('MM/DD/YYYY')}}",
        "text": "Good morning!\n\n📊 DAILY SUMMARY:\n\n🆕 New Leads Yesterday: {{$json['newLeadsCount']}}\n📞 Follow-ups Needed Today: {{$json['followupsCount']}}\n📅 Appointments Today: {{$json['appointmentsCount']}}\n\n---\n\nNEW LEADS:\n{{$json['newLeads'].map(l => `- ${l['Owner Name']} - ${l['Property Address']}`).join('\\n')}}\n\n---\n\nFOLLOW-UPS TODAY:\n{{$json['followups'].map(l => `- ${l['Owner Name']} - ${l['Phone Number']}`).join('\\n')}}\n\n---\n\nGo get 'em!\n\nMy Foreclosure Solution"
      },
      "name": "Send Daily Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [850, 300]
    }
  ]
}
```
{% endraw %}

---

## Workflow 4: SMS Follow-up Automation

**What it does:** Sends text messages to leads who haven't responded to emails.

### Required: Twilio Account
- Sign up: https://www.twilio.com/
- Get a phone number (~$1/month)
- SMS cost: $0.0079 per message

### Workflow:

```
Schedule Trigger (Every 3 hours)
→ Get leads with status "Email Sent"
→ Check if email sent > 24 hours ago
→ Send SMS via Twilio
→ Update status to "SMS Sent"
```

### n8n Workflow JSON:

{% raw %}
```json
{
  "name": "SMS Follow-up After Email",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 3
            }
          ]
        }
      },
      "name": "Schedule - Every 3 Hours",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!A:N"
      },
      "name": "Get Email Sent Leads",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json['Status']}}",
              "operation": "contains",
              "value2": "Email Sent"
            }
          ],
          "dateTime": [
            {
              "value1": "={{$json['Last Contact']}}",
              "operation": "before",
              "value2": "={{$now.minus({hours: 24}).toISO()}}"
            }
          ]
        }
      },
      "name": "Filter - Email > 24hrs Ago",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "fromPhoneNumber": "+1YOUR_TWILIO_NUMBER",
        "toPhoneNumber": "={{$json['Phone Number']}}",
        "message": "Hi {{$json['Owner Name']}}, this is [YOUR NAME] from My Foreclosure Solution. I emailed you about {{$json['Property Address']}}. I can help stop your foreclosure. Free consultation: (949) 565-5285. Reply STOP to opt out."
      },
      "name": "Send SMS via Twilio",
      "type": "n8n-nodes-base.twilio",
      "typeVersion": 1,
      "position": [850, 300]
    },
    {
      "parameters": {
        "sheetId": "1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw",
        "range": "NOD Leads!K{{$json['row']}}",
        "values": {
          "Status": "SMS Sent - {{$now.format('MM/DD/YYYY')}}"
        }
      },
      "name": "Update Status",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [1050, 300]
    }
  ]
}
```
{% endraw %}

---

## Workflow 5: High-Value Lead Alert (Instant Notification)

**What it does:** Instantly notifies you via SMS when a high-equity lead is added to your sheet.

### Workflow:

```
Google Sheets Trigger (New row)
→ Check if Estimated Value > $500,000
→ Calculate equity
→ If equity > $100,000 → Send you urgent SMS
→ Send you email with lead details
```

---

## Advanced Automation Ideas

### 1. **Automatic Property Value Lookup**
- Use Zillow API or RapidAPI
- Auto-populate "Estimated Value" column
- Calculate equity automatically
- Flag high-value leads

### 2. **Voicemail Drop**
- Use Slybroadcast or similar
- Leave pre-recorded voicemail without calling
- Scales to 100+ leads/hour
- Cost: ~$0.05/drop

### 3. **AI Call Transcription**
- Record calls with Rev.ai or Assembly AI
- Auto-transcribe to text
- Save notes to Google Sheet
- Search past conversations

### 4. **Lead Scoring**
- Points for equity amount
- Points for days since NOD
- Points for engagement (opened email, clicked link)
- Auto-prioritize high-scoring leads

### 5. **Drip Campaign Sequences**
```
Day 0: New lead → Send initial email
Day 1: No response → Send SMS
Day 3: No response → Send follow-up email
Day 7: No response → Send value email
Day 14: No response → Final outreach
Day 30: Mark as "Cold Lead"
```

---

## Cost Breakdown

**Free Tier (n8n Cloud):**
- 2,500 workflow executions/month
- Good for 50-100 leads/month
- Cost: $0

**Paid Services:**
- n8n Cloud Pro: $20/month (20,000 executions)
- Twilio (SMS): ~$10/month for 1,000 messages
- Skip Tracing API: $0.15/lead
- Email (SMTP via Gmail): Free

**Total Monthly Cost:** $30-50 for automation of 100-500 leads

**ROI:** 1 deal = $5,000-18,000 = 100-600x ROI

---

## Setup Priority

**Week 1 (Manual):**
- Collect leads manually
- Make calls manually
- Learn the process

**Week 2 (Basic Automation):**
- Set up Workflow 1 (Email Follow-ups)
- Set up Workflow 3 (Daily Report)

**Week 3 (Advanced Automation):**
- Set up Workflow 2 (Skip Tracing)
- Set up Workflow 4 (SMS Follow-up)

**Month 2 (Full Automation):**
- Add drip campaigns
- Add AI transcription
- Add lead scoring
- Hire VA to handle calls while you close deals

---

## Next Steps

1. **Install n8n** (self-hosted or cloud)
2. **Import Workflow 1** (email automation)
3. **Test with 1 lead** to verify it works
4. **Activate and monitor** for 1 week
5. **Add more workflows** as you scale

Want me to create the actual n8n workflow files you can import directly?

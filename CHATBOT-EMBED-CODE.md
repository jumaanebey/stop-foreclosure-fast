# AI Chatbot - Website Embed Instructions

## Overview
The AI Chatbot is a fully functional, OpenAI-powered assistant that qualifies leads 24/7 and saves them to Google Sheets.

**File Location:** `ai-chatbot.html`

---

## Quick Embed (Add to Every Page)

### Method 1: Inline Embed (Recommended)
Add this code **before the closing `</body>` tag** on every page:

```html
<!-- AI Foreclosure Chatbot -->
<script src="https://yourdomain.com/ai-chatbot.html"></script>
```

### Method 2: Direct Copy-Paste
Copy everything from `ai-chatbot.html` and paste it before the closing `</body>` tag on each page.

---

## Configuration Required

Before deploying, update these 2 values in `ai-chatbot.html` (lines 251-252):

### 1. OpenAI API Key
```javascript
OPENAI_API_KEY: 'YOUR_OPENAI_API_KEY_HERE'
```

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste it here
4. **Cost:** ~$0.01-0.03 per conversation

### 2. n8n Webhook URL
```javascript
GOOGLE_SHEET_WEBHOOK: 'YOUR_N8N_WEBHOOK_URL_HERE'
```

**How to get:**
1. Import the "Chatbot to Google Sheets" n8n workflow
2. Copy the webhook URL from the Webhook node
3. Paste it here

---

## What The Chatbot Does

### Conversation Flow:
1. Greets visitor with empathetic message
2. Asks if they're facing foreclosure
3. Determines if they want to keep or sell home
4. Provides helpful information about options
5. Collects contact information:
   - Name
   - Phone number
   - Email
   - Property address
   - Goal (keep/sell/unsure)
6. Saves lead to Google Sheets via n8n
7. Offers free 7-Day Foreclosure Survival Guide

### Features:
- **24/7 availability** - Never miss a lead
- **Empathetic AI** - Uses GPT-4 for natural, caring conversations
- **Mobile responsive** - Works on all devices
- **Lead capture** - Collects structured data
- **Quick replies** - Makes it easy for visitors to respond
- **Beautiful UI** - Professional gradient design
- **Typing indicator** - Shows bot is "thinking"

---

## Pages to Add Chatbot To

Add the chatbot to ALL pages, especially:

✅ **Homepage** (`index.html`)
✅ **California Foreclosure Help** (`california-foreclosure-help.html`)
✅ **FAQ Page** (`faq.html`)
✅ **Emergency Checklist** (`emergency-checklist.html`)
✅ **Free Guide Page** (`free-guide.html`)
✅ **Virtual Consultation** (`virtual-consultation.html`)
✅ **Thank You Pages** (`thank-you.html`, `thank-you-priority.html`)

---

## Testing Instructions

### 1. Local Testing:
```bash
# Open the file directly in browser
open ai-chatbot.html
```

### 2. Test Conversation:
- Click the chat button (bottom right)
- Type: "I received a foreclosure notice"
- Answer the questions
- Fill out the lead form
- Check if data appears in Google Sheets

### 3. Test Scenarios:
- "I want to keep my home"
- "I want to sell my home"
- "What are my options?"
- "How much does this cost?"

---

## Customization Options

### Change Colors:
Find this code (lines 32-33) and modify:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Avatar:
Replace `🤖` (line 238) with any emoji or icon

### Change Name:
Update "Foreclosure Helper" (line 236) to anything you want

### Adjust Response Length:
In OpenAI config (line 277), change `max_tokens`:
```javascript
max_tokens: 200  // Lower = shorter responses, Higher = longer
```

---

## Integration with n8n

The chatbot sends lead data to n8n via webhook:

**Data Sent:**
```json
{
  "name": "John Doe",
  "phone": "(555) 123-4567",
  "email": "john@example.com",
  "propertyAddress": "123 Main St, Los Angeles, CA",
  "situation": "keep",
  "conversationSummary": "Full chat transcript...",
  "timestamp": "2025-10-28T10:30:00.000Z",
  "source": "Website Chatbot"
}
```

**n8n Workflow** will then:
1. Receive webhook data
2. Add lead to Google Sheet
3. Trigger AI Lead Scorer
4. Send you high-priority alert if needed
5. Trigger follow-up automation

---

## Cost Breakdown

**OpenAI API:**
- ~$0.01-0.03 per conversation
- 100 conversations/month = $1-3
- Essentially free

**Hosting:**
- $0 (runs on your existing website)

**Total:** ~$3/month max

---

## Troubleshooting

### Chatbot button doesn't appear:
- Check if script is loaded (view source)
- Check browser console for errors
- Make sure it's before closing `</body>` tag

### Chatbot doesn't respond:
- Check OpenAI API key is valid
- Check API key has credits
- Check browser console for errors

### Leads not saving to Google Sheets:
- Check n8n webhook URL is correct
- Check n8n workflow is active
- Check webhook is accessible (test with Postman)

### Mobile issues:
- Should work automatically
- Check if viewport meta tag exists in page header

---

## Support

For issues:
1. Check browser console for errors (F12 → Console)
2. Verify OpenAI API key and webhook URL
3. Test webhook URL with curl or Postman
4. Check n8n workflow execution logs

---

## Next Steps

After embedding chatbot:

1. ✅ Import n8n workflows
2. ✅ Connect to Google Sheets
3. ✅ Set up email notifications
4. ✅ Test end-to-end flow
5. ✅ Monitor conversations
6. ✅ Optimize based on common questions

The chatbot will start capturing leads immediately!

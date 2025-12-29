# Vapi Voice AI Setup Guide

## What is Vapi?

Vapi.ai is an AI voice agent platform that can make outbound calls to your leads. The AI sounds natural and can handle conversations, book appointments, and qualify leads.

**Cost:** ~$0.05-0.10 per minute of call time

---

## Step 1: Create Vapi Account

1. Go to https://vapi.ai
2. Sign up for free account
3. Add credits ($10 minimum to start)

---

## Step 2: Get a Phone Number

1. In Vapi dashboard, go to **Phone Numbers**
2. Click **Buy Number**
3. Choose a local California number (949 area code recommended)
4. Cost: ~$2/month

---

## Step 3: Create Your Assistant

1. Go to **Assistants** → **Create Assistant**
2. Use these settings:

### Basic Settings
```
Name: Foreclosure Helper
Model: gpt-4-turbo (or gpt-3.5-turbo for cheaper)
Voice: rachel (female, professional) or josh (male, friendly)
```

### System Prompt
```
You are Sarah, a friendly and empathetic assistant calling on behalf of My Foreclosure Solution. You're reaching out to homeowners who may be facing foreclosure.

Your goal is to:
1. Introduce yourself warmly
2. Acknowledge their situation with empathy
3. Explain that you can help them explore options
4. Try to schedule a free consultation call

Key points to make:
- We help California homeowners stop foreclosure
- Free consultation, no obligation
- We've helped hundreds of families
- They have more options than they might think
- Time is important - the sooner they act, the more options they have

If they're interested: Offer to have the owner call them back at (949) 565-5285 or schedule through our calendar.

If they're not interested: Thank them politely and wish them well.

Be conversational, not salesy. Listen more than you talk. Show genuine care.

Variables available:
- {{customerName}}: The homeowner's first name
- {{propertyAddress}}: Their property address
- {{agentName}}: Your name (Sarah)
- {{companyName}}: My Foreclosure Solution
- {{callbackNumber}}: (949) 565-5285
```

### First Message
```
Hi, is this {{customerName}}? This is Sarah calling from My Foreclosure Solution. I'm reaching out about the property on {{propertyAddress}}. Do you have just a minute?
```

### End Call Phrases
```
- "I'm not interested"
- "Take me off your list"
- "Don't call again"
- "I'm working with someone else"
```

---

## Step 4: Configure n8n Integration

### Get Your API Key
1. In Vapi dashboard, go to **Settings** → **API Keys**
2. Create new key
3. Copy the key

### Add to n8n
1. In n8n, go to **Credentials** → **Add Credential**
2. Select **Header Auth**
3. Name: `Vapi API Key`
4. Header Name: `Authorization`
5. Header Value: `Bearer YOUR_API_KEY_HERE`

### Get Your IDs
From Vapi dashboard, copy:
- **Phone Number ID**: Found in Phone Numbers section
- **Assistant ID**: Found in Assistants section

### Update Workflow
In `9-voice-ai-caller.json`, replace:
- `YOUR_VAPI_PHONE_NUMBER_ID` → Your actual phone number ID
- `YOUR_VAPI_ASSISTANT_ID` → Your actual assistant ID

---

## Step 5: Test Your Setup

1. In n8n, open the Voice AI workflow
2. Click **Execute Workflow** manually
3. Add a test lead to your sheet with your own phone number
4. Wait for the call

---

## Call Compliance

### Required Disclosures
- Identify as AI within first 30 seconds
- Provide callback number
- Honor opt-out requests immediately

### Best Practices
- Only call 9 AM - 8 PM local time
- Max 10 calls per batch
- Don't call same person twice in 24 hours
- Keep call records for 2 years

### TCPA Compliance
- Only call leads who submitted their info (consent)
- Honor Do Not Call requests
- Include opt-out in any follow-up SMS

---

## Cost Estimate

| Volume | Monthly Cost |
|--------|--------------|
| 50 calls/month | ~$15-25 |
| 100 calls/month | ~$30-50 |
| 200 calls/month | ~$60-100 |

*Assumes average 3-minute call*

---

## Troubleshooting

### Calls not going through?
- Check phone number is active
- Verify API key is correct
- Ensure credits in Vapi account

### AI sounds robotic?
- Try different voice (Rachel, Josh, or Ava)
- Adjust speech speed in assistant settings

### Calls getting hung up on?
- Review system prompt for naturalness
- Make first message shorter
- Add more pauses in speech

---

## Next Steps

1. ✅ Create Vapi account
2. ✅ Buy phone number
3. ✅ Create assistant with script above
4. ✅ Add credentials to n8n
5. ✅ Update workflow with your IDs
6. ✅ Test with your own phone
7. ✅ Activate workflow
8. ✅ Monitor calls in Vapi dashboard

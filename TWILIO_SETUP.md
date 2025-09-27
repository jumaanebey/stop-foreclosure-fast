# 📱 Twilio SMS Setup Instructions

## ✅ Your SMS System is Ready!

The SMS follow-up sequence is now connected to Twilio. Here's how to activate it:

## 1️⃣ Add Your Twilio Credentials

Edit your `.env` file and add:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE=+19493284811
```

Get these from: https://console.twilio.com

## 2️⃣ Start the Server

```bash
cd ~/Documents/stop-foreclosure-fast/google-ai-setup
source ../.env  # Load environment variables
node server.js
```

## 3️⃣ How It Works

When someone fills out your form with SMS consent:

**Immediate (0 min):**
"Hi [Name], I got your urgent foreclosure request..."

**Follow-up (5 min):**
"[Name], I'm ready to discuss your foreclosure options right now..."

**Urgent (30 min):**
"URGENT for [Name]: With your auction approaching, we need to act TODAY..."

## 4️⃣ Special Features

- **7-day auctions** get extra urgent follow-ups
- **Personalized messages** with lead's name
- **Fallback to Google Apps Script** if Twilio fails
- **All messages logged** for tracking

## 5️⃣ Testing

1. Fill out form on your website
2. Check "Yes, text me" box
3. Submit form
4. Watch SMS arrive immediately!

## 📊 SMS Benefits

- **3x higher response rate** than calls alone
- **Instant connection** while lead is hot
- **Multiple touchpoints** prevent cooling off
- **Text-preferred** customers reached

## 🚨 Important

- Twilio costs ~$0.0075 per SMS
- Always include opt-out instructions
- Follow TCPA compliance rules
- Test with your own number first

Your website now has enterprise-level SMS follow-up! 🚀
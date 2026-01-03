# 📱 Update Google Apps Script for iPhone Alerts

## ✅ Your iPhone Alert System is Ready!

The website now sends instant lead alerts directly to your iPhone via AT&T's email-to-SMS gateway.

## 🔄 Update Your Google Apps Script

1. **Go to**: https://script.google.com/macros/s/AKfycbwot6SWKdQKzoOmVizO8_mh93aU_A6cIkGnpu5yrnzmPrfkn4pDQ7E07asi1_PXSpsq/edit

2. **Replace the entire Code.gs file** with the updated version from:
   `/Documents/stop-foreclosure-fast/google-apps-script-convertkit.js`

3. **Save** the script (Ctrl+S / Cmd+S)

4. **Deploy** → Manage deployments → Edit → Deploy

## 📱 How iPhone Alerts Work

When someone fills out your foreclosure form:

1. **Instant iPhone SMS**: `🚨 URGENT FORECLOSURE LEAD`
   - Name, phone, property details
   - Timeline urgency level
   - Call-to-action

2. **Backup Email**: Sent to jumaanebey@gmail.com
   - Complete lead details
   - Confirmation that SMS was sent

3. **Google Sheets**: Lead automatically saved
4. **ConvertKit**: Email follow-up sequence triggered

## 📲 SMS Format Example

```
🚨 URGENT FORECLOSURE LEAD
📞 John Smith
📱 (555) 123-4567
🏠 123 Main St, CA
⏰ Sale: 7days
💰 Value: $500,000
📍 Action: Call immediately!

Captured: 12/26/2024, 3:45 PM
```

## 🔧 Technical Details

- **SMS Gateway**: 9495655285@txt.att.com
- **Character Limit**: 160 chars (automatically truncated)
- **Delivery**: Usually instant, max 1-2 minutes
- **Fallback**: Email if SMS fails
- **Cost**: Free via AT&T email-to-SMS

## ✅ Testing

1. Fill out form on your website
2. Check iPhone for immediate SMS
3. Check email for backup confirmation
4. Verify lead appears in Google Sheets

Your foreclosure website now has instant iPhone notifications! 🚀
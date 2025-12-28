# 📧 Email Automation Setup Guide

## 🎯 What This Does:
- **Automatic PDF delivery** when someone downloads your guide
- **Instant email confirmations** for consultation requests
- **Lead notifications** sent to you immediately
- **Professional email templates** with your branding

---

## 📋 Step-by-Step Setup Instructions

### STEP 1: Create Your PDF Guide
1. Use the content from `PDF_CONTENT_TEMPLATE.md`
2. Create PDF using Canva or Google Docs
3. Upload to Google Drive
4. **Get the File ID** from the URL: `https://drive.google.com/file/d/FILE_ID_HERE/view`
5. **Make it public**: Right-click → Share → Anyone with link can view

### STEP 2: Set Up Google Apps Script
1. Go to [script.google.com](https://script.google.com)
2. Click "New Project"
3. Delete existing code
4. Copy ALL code from `google-apps-script.js`
5. Paste into the editor

### STEP 3: Configure Your Settings
Update these values at the top of the script:

```javascript
const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'; // From your Google Sheet URL
const PDF_FILE_ID = 'YOUR_PDF_FILE_ID'; // From Google Drive (Step 1)
const YOUR_EMAIL = 'help@myforeclosuresolutions.com'; // Your notification email
```

### STEP 4: Deploy the Script
1. Click "Deploy" → "New Deployment"
2. Type: "Web app"
3. Execute as: "Me"
4. Who has access: "Anyone"
5. Click "Deploy"
6. **Copy the Web App URL** (you'll need this!)
7. Click "Authorize access" and approve permissions

### STEP 5: Update Your Website Forms
Replace the old Google Apps Script URL in your forms:

**In `free-guide.html` (line 476):**
```javascript
fetch('YOUR_NEW_WEB_APP_URL_HERE', {
```

**In `index.html` if you have any custom forms:**
Update the fetch URL to your new deployment.

### STEP 6: Test the System
1. Submit your lead magnet form with a test email
2. Check that you receive:
   - ✅ PDF guide email (to the test email)
   - ✅ Lead notification (to your email)
   - ✅ Data logged in Google Sheet

---

## 📧 Email Templates Included

### 1. PDF Guide Delivery Email
- **Subject**: "Your FREE 7-Day Foreclosure Survival Guide - [Name]"
- **Includes**: PDF attachment + call-to-action
- **Design**: Professional HTML with your branding

### 2. Consultation Confirmation
- **Subject**: "We received your request - [Name]"
- **Features**: Emergency detection + next steps
- **Purpose**: Builds confidence and sets expectations

### 3. Lead Notifications (To You)
- **Subject**: "New lead_magnet submission - [Name]"
- **Includes**: All lead details + urgency flags
- **Purpose**: Immediate follow-up alerts

---

## 🔧 Troubleshooting

### "Permission denied" error:
- Make sure your PDF is set to "Anyone with link can view"
- Re-run the authorization process in Apps Script

### Emails not sending:
- Check spam folder
- Verify email addresses in script configuration
- Test with `testEmailDelivery()` function

### PDF not attaching:
- Confirm PDF_FILE_ID is correct
- Make sure PDF is shared publicly
- Check file size (Gmail limit: 25MB)

### Form submissions not working:
- Verify the Web App URL is updated in your forms
- Check that deployment is set to "Anyone" access
- Test the Apps Script URL directly

---

## 📊 What Gets Tracked

### In Your Google Sheet:
- Timestamp
- Type (lead_magnet or consultation)
- Name, Email, Phone
- Property Address
- Situation details
- Timeline/urgency
- Source (website, ads, etc.)
- Status (New Lead)

### Email Analytics:
- Open rates (use email service for detailed analytics)
- Click-through rates on phone/CTA buttons
- Response times to your follow-up

---

## 🚀 Next Level Improvements

### Option 1: Email Service Integration
Instead of Gmail, use ConvertKit/Mailchimp for:
- Better deliverability
- Open/click tracking
- Automated sequences
- A/B testing

### Option 2: CRM Integration
Connect to:
- HubSpot (free CRM)
- Pipedrive
- Salesforce
- Custom database

### Option 3: Advanced Automation
- SMS notifications for urgent leads
- Automatic follow-up sequences
- Lead scoring based on responses
- Calendar booking integration

---

## ⚡ Quick Test Checklist

Before going live:
- [ ] PDF uploads correctly to Google Drive
- [ ] PDF is publicly accessible
- [ ] Apps Script deployed successfully
- [ ] Website forms use new URL
- [ ] Test submission sends PDF
- [ ] You receive lead notifications
- [ ] Data appears in Google Sheet
- [ ] All email templates look professional

---

## 🆘 Support

If you run into issues:
1. Check the Apps Script execution log
2. Verify all URLs and IDs are correct
3. Test each component individually
4. Check spam folders for emails

Your email automation is now ready to convert leads 24/7!
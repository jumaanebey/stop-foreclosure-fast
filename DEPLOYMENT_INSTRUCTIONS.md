# Google Apps Script Deployment Instructions

## Step 1: Create Google Sheet ✅
1. Go to https://sheets.google.com
2. Create new blank spreadsheet
3. Name it: "Foreclosure Leads - MyForeclosureSolution.com"
4. Copy the Spreadsheet ID from URL (between `/d/` and `/edit`)

## Step 2: Create Google Apps Script Project
1. Go to https://script.google.com
2. Click "+ New project"
3. Name it: "Foreclosure Lead Automation"
4. Delete the default code in Code.gs
5. Copy ALL code from `google-apps-script.js` (in this folder)
6. Paste it into Code.gs
7. **IMPORTANT:** Update line 15 with your Spreadsheet ID:
   ```javascript
   const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';
   ```

## Step 3: Deploy as Web App
1. Click "Deploy" → "New deployment"
2. Click gear icon ⚙️ → Select "Web app"
3. Configure settings:
   - **Description:** "Foreclosure lead capture system"
   - **Execute as:** Me (your-email@gmail.com)
   - **Who has access:** Anyone
4. Click "Deploy"
5. **Authorize the app:**
   - Click "Authorize access"
   - Choose your Google account
   - Click "Advanced" → "Go to Foreclosure Lead Automation (unsafe)"
   - Click "Allow"
6. **COPY THE WEB APP URL** (looks like: https://script.google.com/macros/s/LONG_ID/exec)

## Step 4: Test the System
1. Open `test-email-system.html` in your browser
2. Paste the Web App URL
3. Enter your email address for testing
4. Run both tests (Lead Magnet + Consultation)
5. Check your inbox for:
   - PDF guide email (with attachment)
   - Consultation confirmation
   - Notification emails at help@myforeclosuresolutions.com

## Step 5: Update Live Website
1. Open `free-guide.html`
2. Find line 491
3. Replace the URL with your new Web App URL
4. Save and commit changes
5. Push to GitHub to deploy

## Troubleshooting

### If emails don't arrive:
- Check spam folder
- Verify PDF file ID is correct in Apps Script line 16
- Check Apps Script logs: View → Executions

### If "Permission Denied" error:
- Re-authorize the app in Apps Script
- Make sure "Execute as: Me" is selected

### If data doesn't appear in Sheet:
- Verify Spreadsheet ID is correct
- Check that sheet is not protected/read-only

## Success Checklist
- [ ] Google Sheet created
- [ ] Apps Script deployed as Web App
- [ ] Test emails received with PDF attachment
- [ ] Test data appears in Google Sheet
- [ ] Notification emails received
- [ ] Live website updated with Web App URL

---

**Need help?** Check Apps Script logs or test again with the dashboard.

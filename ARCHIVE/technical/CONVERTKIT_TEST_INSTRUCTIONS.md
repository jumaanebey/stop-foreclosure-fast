# ConvertKit Integration Test Instructions

## What to Test
Test all 4 lead capture methods to ensure they're properly integrated with ConvertKit:

### 1. Emergency Contact Popup
- Click the red "Stop Foreclosure NOW" button on homepage
- Fill out the emergency contact form that appears after SMS link
- Check that submission goes to Google Sheets with `type: 'emergency_help'`
- Verify it triggers urgent email sequence in ConvertKit

### 2. Exit Intent Popup  
- Trigger exit intent popup (try `testExitPopup()` in browser console)
- Fill out the popup form with checkbox options
- Check Google Sheets for `type: 'exit_intent_popup'`
- Should add to general ConvertKit form

### 3. Lead Magnet Form
- Scroll to "Free Download: California Foreclosure Timeline Checklist" section
- Fill out the form
- Should redirect to checklist-download.html
- Check Google Sheets for `type: 'lead_magnet'`

### 4. Main Contact Form
- Scroll to "Get Your Free Cash Offer Today" section
- Fill out the complete contact form
- Should redirect to thank-you.html (if it exists) or show success
- Check Google Sheets for `type: 'contact'`

## How to Test

### Option 1: Real Test (Recommended)
1. Go to https://myforeclosuresolution.com
2. Use a real email address you can check
3. Fill out one form completely
4. Check:
   - Google Sheets for the entry
   - ConvertKit dashboard for the new subscriber
   - Your email for confirmation/sequence emails

### Option 2: Local Test
1. Open index.html in browser
2. Fill out forms with test data
3. Check browser console for any JavaScript errors
4. Verify form submissions attempt to reach Google Apps Script

## What to Look For

✅ **Success Indicators:**
- Form submission completes without errors
- Redirect happens correctly  
- Data appears in Google Sheets
- ConvertKit shows new subscriber
- Urgent leads trigger notifications

❌ **Problems to Watch For:**
- JavaScript errors in console
- Forms don't submit
- No redirect after submission  
- Missing data in Google Sheets
- ConvertKit not receiving subscribers
- No email sequences triggered

## ConvertKit Dashboard Locations

1. **Forms**: https://app.kit.com/forms
2. **Sequences**: https://app.kit.com/sequences  
3. **Subscribers**: https://app.kit.com/subscribers
4. **Reporting**: https://app.kit.com/reports

## Google Sheets Location
Check your Google Sheets dashboard for the foreclosure leads sheet (ID: 1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU)

## Current Google Apps Script Deployment
URL: https://script.google.com/macros/s/AKfycbwot6SWKdQKzoOmVizO8_mh93aU_A6cIkGnpu5yrnzmPrfkn4pDQ7E07asi1_PXSpsq/exec

## Urgent Lead Detection
The system should automatically detect urgent leads based on:
- `type: 'emergency_help'`
- `timeline: 'immediate'` 
- `foreclosure_status: 'yes'`
- Checkbox selections indicating urgency

These should trigger:
1. Email notification to jumaanebey@gmail.com
2. Enrollment in ConvertKit urgent sequence (ID: 2459120)
3. Immediate response priority
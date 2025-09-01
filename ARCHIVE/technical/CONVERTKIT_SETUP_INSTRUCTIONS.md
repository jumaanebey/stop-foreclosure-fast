# ConvertKit Integration Setup Instructions

## Step 1: Update Google Apps Script

1. Go to https://script.google.com
2. Open your existing project (ID: 1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU)
3. Replace the entire Code.gs content with the updated code from `google-apps-script-convertkit.js`

## Step 2: Test Basic API Connection

1. In Google Apps Script, run the function: `testBasicConvertKitAPI`
2. Check the execution log for results
3. Look for response code 200 (success) or error messages

## Step 3: Test Full Integration

1. Run the function: `testConvertKitConnection`
2. Check if subscriber is added to ConvertKit
3. Verify tags are applied correctly

## Step 4: Deploy Updated Script

1. Click "Deploy" → "New deployment"
2. Choose type: "Web app"
3. Execute as: "Me"
4. Who has access: "Anyone"
5. Copy the new deployment URL

## Step 5: Update Website Forms

1. Replace the Google Apps Script URL in `js/script.js` with the new deployment URL
2. Test form submissions from your live website

## Expected Results

✅ **Success indicators:**
- Response code 200 from ConvertKit API
- New subscriber appears in ConvertKit dashboard
- Tags are applied to subscriber
- Email sequences start automatically

❌ **Failure indicators:**
- 404 errors → API endpoint issue
- 401 errors → Authentication issue  
- 422 errors → Data validation issue

## Troubleshooting

### If you get 404 errors:
- Verify API key is correct
- Check ConvertKit account is active
- Try API v3 vs v4 endpoints

### If you get 401 errors:
- Double-check API key and secret
- Ensure ConvertKit account has API access enabled

### If you get 422 errors:
- Check email format is valid
- Verify required fields are present

## Next Steps After Success

1. Create ConvertKit forms for different lead types
2. Set up email sequences for each form
3. Configure automated tagging rules
4. Test complete lead-to-email flow

## Contact for Help

If issues persist, check:
1. ConvertKit API documentation
2. Google Apps Script logs
3. Browser network tab for CORS errors
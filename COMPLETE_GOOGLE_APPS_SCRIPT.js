// ===== COMPLETE GOOGLE APPS SCRIPT FOR CONVERTKIT INTEGRATION =====
// Copy this entire code into your Google Apps Script Code.gs file

// ============ CONFIGURATION ============
var CONVERTKIT_API_KEY = 'Hh9PtQFOyWkQN4SZ3w0iXA';
var CONVERTKIT_API_SECRET = 't1mpiB_IoR99DjTudHfQ25yF00U8uAAXepwbu0CsDn4';
var GOOGLE_SHEET_ID = '1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU';
var NOTIFICATION_EMAIL = 'jumaanebey@gmail.com';
var CONVERTKIT_FORM_ID = '8430004';

// ============ MAIN FORM HANDLER ============
function doPost(e) {
  try {
    console.log('Form submission received');
    
    // Parse form data
    var data = JSON.parse(e.postData.contents);
    console.log('Data received: ' + JSON.stringify(data));
    
    // Save to Google Sheets
    saveToGoogleSheets(data);
    console.log('Saved to Google Sheets');
    
    // Add to ConvertKit
    if (data.email) {
      console.log('Adding to ConvertKit: ' + data.email);
      var result = addToConvertKitSimple(data.email, data.name);
      console.log('ConvertKit result: ' + result);
    }
    
    // Send urgent notification if needed
    if (isUrgentLead(data)) {
      sendUrgentNotification(data);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.log('Error in doPost: ' + error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ============ GOOGLE SHEETS FUNCTIONS ============
function saveToGoogleSheets(data) {
  var sheet = SpreadsheetApp.openById(GOOGLE_SHEET_ID).getActiveSheet();
  
  // Create headers if sheet is empty
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, 12).setValues([[
      'Timestamp', 'Type', 'Name', 'Email', 'Phone', 'Property Address',
      'Desired Price', 'Property Type', 'Condition', 'Timeline', 
      'Foreclosure Status', 'Best Time to Call'
    ]]);
  }
  
  // Add the new lead data
  sheet.appendRow([
    new Date(),
    data.type || 'contact',
    data.name || '',
    data.email || '',
    data.phone || '',
    data.property_address || data.address || '',
    data.desired_price || '',
    data.property_type || '',
    data.property_condition || '',
    data.timeline || '',
    data.foreclosure_status || '',
    data.best_time || ''
  ]);
  
  console.log('Data saved to Google Sheets');
}

// ============ CONVERTKIT INTEGRATION ============
function addToConvertKitSimple(email, name) {
  var url = 'https://api.convertkit.com/v3/forms/' + CONVERTKIT_FORM_ID + '/subscribe';
  
  var payload = {
    api_key: CONVERTKIT_API_KEY,
    email: email,
    first_name: name ? name.split(' ')[0] : ''
  };
  
  try {
    console.log('ConvertKit API Call - Email: ' + email);
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    console.log('ConvertKit Response Code: ' + responseCode);
    console.log('ConvertKit Response Text: ' + responseText);
    
    if (responseCode === 200) {
      console.log('SUCCESS: Added to ConvertKit');
      return 'success';
    } else {
      console.log('FAILED: ConvertKit returned ' + responseCode);
      return 'failed';
    }
  } catch (error) {
    console.log('ConvertKit Error: ' + error.toString());
    return 'error';
  }
}

// ============ HELPER FUNCTIONS ============
function isUrgentLead(data) {
  return data.timeline === 'immediate' || 
         data.foreclosure_status === 'yes' ||
         data.type === 'emergency_help';
}

function sendUrgentNotification(data) {
  var subject = '🚨 URGENT FORECLOSURE LEAD: ' + (data.name || 'New Lead');
  
  var body = 'URGENT FORECLOSURE LEAD RECEIVED\n\n' +
             'Name: ' + (data.name || 'Not provided') + '\n' +
             'Email: ' + (data.email || 'Not provided') + '\n' +
             'Phone: ' + (data.phone || 'Not provided') + '\n' +
             'Property: ' + (data.property_address || data.address || 'Not provided') + '\n' +
             'Desired Price: ' + (data.desired_price ? '$' + data.desired_price : 'Not provided') + '\n' +
             'Timeline: ' + (data.timeline || 'Not provided') + '\n' +
             'Foreclosure Status: ' + (data.foreclosure_status || 'Not provided') + '\n' +
             'Lead Source: ' + (data.type || 'Unknown') + '\n\n' +
             'ACTION REQUIRED: Contact this lead immediately!\n\n' +
             'Time received: ' + new Date().toLocaleString();

  try {
    GmailApp.sendEmail(NOTIFICATION_EMAIL, subject, body);
    console.log('Urgent notification sent');
  } catch (error) {
    console.log('Failed to send notification: ' + error.toString());
  }
}

// ============ TEST FUNCTIONS ============
function simpleConvertKitTest() {
  var url = 'https://api.convertkit.com/v3/forms/' + CONVERTKIT_FORM_ID + '/subscribe';
  
  var payload = {
    api_key: CONVERTKIT_API_KEY,
    email: 'test' + Date.now() + '@example.com',
    first_name: 'TestUser'
  };
  
  try {
    console.log('Testing ConvertKit with email: ' + payload.email);
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    console.log('Response Code: ' + response.getResponseCode());
    console.log('Response: ' + response.getContentText());
    
    if (response.getResponseCode() === 200) {
      console.log('SUCCESS! Subscriber added to ConvertKit');
      return true;
    } else {
      console.log('FAILED! Check response above');
      return false;
    }
  } catch (error) {
    console.log('ERROR: ' + error.toString());
    return false;
  }
}

function testWithRealEmail() {
  var url = 'https://api.convertkit.com/v3/forms/' + CONVERTKIT_FORM_ID + '/subscribe';
  
  var payload = {
    api_key: CONVERTKIT_API_KEY,
    email: 'jumaanebey@gmail.com',
    first_name: 'Jumaane'
  };
  
  try {
    console.log('Testing with real email: jumaanebey@gmail.com');
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    console.log('Response Code: ' + response.getResponseCode());
    console.log('Response: ' + response.getContentText());
    
  } catch (error) {
    console.log('Error: ' + error.toString());
  }
}

function testAPIAccount() {
  var url = 'https://api.convertkit.com/v3/account?api_key=' + CONVERTKIT_API_KEY;
  
  try {
    console.log('Testing API account connection...');
    var response = UrlFetchApp.fetch(url);
    console.log('Account Response: ' + response.getContentText());
  } catch (error) {
    console.log('Account Error: ' + error.toString());
  }
}

function testFixedAPI() {
  var url = 'https://api.convertkit.com/v3/forms/' + CONVERTKIT_FORM_ID + '/subscribe';
  var testEmail = 'apitest' + Date.now() + '@test.com';
  
  var payload = {
    api_key: CONVERTKIT_API_KEY,
    email: testEmail,
    first_name: 'API Test'
  };
  
  try {
    console.log('Testing fixed API integration with: ' + testEmail);
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      payload: 'api_key=' + CONVERTKIT_API_KEY + '&email=' + testEmail + '&first_name=API Test'
    });
    
    console.log('Response Code: ' + response.getResponseCode());
    console.log('Response: ' + response.getContentText());
    
  } catch (error) {
    console.log('Error: ' + error.toString());
  }
}

// ============ MANUAL TESTS FOR DEBUGGING ============
function testFormSubmission() {
  // Simulate a website form submission
  var testData = {
    type: 'cash_offer_request',
    name: 'John Test',
    email: 'johntest' + Date.now() + '@example.com',
    phone: '555-123-4567',
    property_address: '123 Test St, Los Angeles, CA',
    desired_price: '500000',
    timeline: 'fast',
    foreclosure_status: 'yes'
  };
  
  console.log('Testing complete form submission...');
  
  // Save to sheets
  saveToGoogleSheets(testData);
  
  // Add to ConvertKit
  var result = addToConvertKitSimple(testData.email, testData.name);
  console.log('Form submission test result: ' + result);
  
  return result;
}

// ============ DEPLOYMENT INSTRUCTIONS ============
/*
DEPLOYMENT STEPS:

1. REPLACE YOUR CODE.GS:
   - Delete all existing code in your Google Apps Script
   - Copy and paste this entire file content
   - Save the script

2. TEST THE INTEGRATION:
   - Run 'simpleConvertKitTest' function
   - Check execution logs for success
   - Verify subscriber appears in ConvertKit

3. DEPLOY AS WEB APP:
   - Click "Deploy" → "New deployment"
   - Type: "Web app"
   - Execute as: "Me"
   - Who has access: "Anyone"
   - Click "Deploy"
   - Copy the deployment URL

4. UPDATE YOUR WEBSITE:
   - Replace GOOGLE_SCRIPT_URL in js/script.js
   - Replace GOOGLE_SCRIPT_URL in js/calculator.js
   - Commit and push changes

5. TEST LIVE FORMS:
   - Submit forms on your website
   - Check Google Apps Script executions
   - Verify ConvertKit gets new subscribers

TROUBLESHOOTING:
- Run 'testAPIAccount' to verify API credentials
- Run 'testFormSubmission' to test complete flow
- Check execution logs for detailed error messages
*/
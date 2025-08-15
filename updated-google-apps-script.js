// ===== UPDATED GOOGLE APPS SCRIPT WITH SEQUENCE INTEGRATION =====
// Replace your existing Code.gs with this updated version

// ============ CONFIGURATION ============
var CONVERTKIT_API_KEY = 'Hh9PtQFOyWkQN4SZ3w0iXA';
var CONVERTKIT_API_SECRET = 't1mpiB_IoR99DjTudHfQ25yF00U8uAAXepwbu0CsDn4';
var GOOGLE_SHEET_ID = '1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU';
var NOTIFICATION_EMAIL = 'jumaanebey@gmail.com';
var CONVERTKIT_FORM_ID = '8430004';

// ConvertKit Sequence IDs
var URGENT_FORECLOSURE_SEQUENCE = '2459120';
// Add more sequence IDs here when you create them:
// var CASH_OFFER_SEQUENCE = 'YOUR_CASH_OFFER_SEQUENCE_ID';
// var LEAD_MAGNET_SEQUENCE = 'YOUR_LEAD_MAGNET_SEQUENCE_ID';

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
    
    // Add to ConvertKit with sequence enrollment
    if (data.email) {
      console.log('Adding to ConvertKit: ' + data.email);
      var result = addToConvertKitWithSequence(data.email, data.name, data.type);
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

// ============ CONVERTKIT INTEGRATION WITH SEQUENCES ============
function addToConvertKitWithSequence(email, name, leadType) {
  // First add to general form
  var formResult = addToConvertKitForm(email, name);
  
  // Then add to appropriate sequence if urgent
  if (isUrgentLeadType(leadType)) {
    var sequenceResult = addToSequence(email, name, URGENT_FORECLOSURE_SEQUENCE);
    console.log('Added to urgent sequence: ' + sequenceResult);
  }
  
  return formResult;
}

function addToConvertKitForm(email, name) {
  var url = 'https://api.convertkit.com/v3/forms/' + CONVERTKIT_FORM_ID + '/subscribe';
  
  var payload = {
    api_key: CONVERTKIT_API_KEY,
    email: email,
    first_name: name ? name.split(' ')[0] : ''
  };
  
  try {
    console.log('ConvertKit Form API Call - Email: ' + email);
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    console.log('ConvertKit Form Response Code: ' + responseCode);
    console.log('ConvertKit Form Response Text: ' + responseText);
    
    if (responseCode === 200) {
      console.log('SUCCESS: Added to ConvertKit form');
      return 'success';
    } else {
      console.log('FAILED: ConvertKit form returned ' + responseCode);
      return 'failed';
    }
  } catch (error) {
    console.log('ConvertKit Form Error: ' + error.toString());
    return 'error';
  }
}

function addToSequence(email, name, sequenceId) {
  var url = 'https://api.convertkit.com/v3/sequences/' + sequenceId + '/subscribe';
  
  var payload = {
    api_secret: CONVERTKIT_API_SECRET,
    email: email,
    first_name: name ? name.split(' ')[0] : ''
  };
  
  try {
    console.log('Adding to sequence ' + sequenceId + ' - Email: ' + email);
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    console.log('Sequence Response Code: ' + responseCode);
    console.log('Sequence Response Text: ' + responseText);
    
    if (responseCode === 200) {
      console.log('SUCCESS: Added to sequence ' + sequenceId);
      return 'success';
    } else {
      console.log('FAILED: Sequence returned ' + responseCode);
      return 'failed';
    }
  } catch (error) {
    console.log('Sequence Error: ' + error.toString());
    return 'error';
  }
}

// ============ HELPER FUNCTIONS ============
function isUrgentLead(data) {
  return data.timeline === 'immediate' || 
         data.foreclosure_status === 'yes' ||
         data.type === 'emergency_help' ||
         data.type === 'foreclosure_urgent';
}

function isUrgentLeadType(leadType) {
  return leadType === 'emergency_help' ||
         leadType === 'foreclosure_urgent' ||
         leadType === 'contact'; // Assume general contact might be urgent
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
function testUrgentSequence() {
  var testEmail = 'test' + Date.now() + '@example.com';
  var result = addToSequence(testEmail, 'Test User', URGENT_FORECLOSURE_SEQUENCE);
  console.log('Test urgent sequence result: ' + result);
  return result;
}

function testCompleteUrgentFlow() {
  var testData = {
    type: 'emergency_help',
    name: 'John Urgent',
    email: 'urgenttest' + Date.now() + '@example.com',
    phone: '555-123-4567',
    property_address: '123 Urgent St, Los Angeles, CA',
    timeline: 'immediate',
    foreclosure_status: 'yes'
  };
  
  console.log('Testing complete urgent flow...');
  
  // Save to sheets
  saveToGoogleSheets(testData);
  
  // Add to ConvertKit with sequence
  var result = addToConvertKitWithSequence(testData.email, testData.name, testData.type);
  console.log('Complete urgent flow test result: ' + result);
  
  return result;
}
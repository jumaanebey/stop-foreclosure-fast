// UPDATED CONVERTKIT INTEGRATION - FIXED VERSION
// Replace your existing ConvertKit functions with these:

// ============ FIXED CONVERTKIT INTEGRATION ============
function addToConvertKitWithSequence(email, name, leadType) {
  console.log('Starting ConvertKit integration for: ' + email + ', type: ' + leadType);
  
  // First add to general form
  var formResult = addToConvertKitForm(email, name);
  console.log('Form result: ' + formResult);
  
  // Then add to appropriate sequence if urgent
  if (isUrgentLeadType(leadType)) {
    console.log('Detected urgent lead, adding to sequence');
    var sequenceResult = addToSequence(email, name, URGENT_FORECLOSURE_SEQUENCE);
    console.log('Sequence result: ' + sequenceResult);
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
    console.log('ConvertKit Form API Call - URL: ' + url);
    console.log('ConvertKit Form API Call - Payload: ' + JSON.stringify(payload));
    
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'User-Agent': 'MyForeclosureSolution/1.0'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    console.log('ConvertKit Form Response Code: ' + responseCode);
    console.log('ConvertKit Form Response Text: ' + responseText);
    
    if (responseCode === 200) {
      console.log('SUCCESS: Added to ConvertKit form');
      return 'success';
    } else {
      console.log('FAILED: ConvertKit form returned ' + responseCode + ' - ' + responseText);
      return 'failed: ' + responseCode;
    }
  } catch (error) {
    console.log('ConvertKit Form Error: ' + error.toString());
    return 'error: ' + error.toString();
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
    console.log('Adding to sequence ' + sequenceId + ' - URL: ' + url);
    console.log('Sequence payload: ' + JSON.stringify(payload));
    
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'User-Agent': 'MyForeclosureSolution/1.0'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    console.log('Sequence Response Code: ' + responseCode);
    console.log('Sequence Response Text: ' + responseText);
    
    if (responseCode === 200) {
      console.log('SUCCESS: Added to sequence ' + sequenceId);
      return 'success';
    } else {
      console.log('FAILED: Sequence returned ' + responseCode + ' - ' + responseText);
      return 'failed: ' + responseCode;
    }
  } catch (error) {
    console.log('Sequence Error: ' + error.toString());
    return 'error: ' + error.toString();
  }
}

// ============ SIMPLE TEST FUNCTION ============
function testConvertKitConnection() {
  console.log('=== TESTING CONVERTKIT CONNECTION ===');
  
  var testEmail = 'jumaanebey+test' + Date.now() + '@gmail.com';
  var testName = 'Test User';
  
  console.log('Testing with email: ' + testEmail);
  console.log('API Key: ' + CONVERTKIT_API_KEY);
  console.log('Form ID: ' + CONVERTKIT_FORM_ID);
  console.log('Sequence ID: ' + URGENT_FORECLOSURE_SEQUENCE);
  
  // Test form addition
  var formResult = addToConvertKitForm(testEmail, testName);
  console.log('Final form result: ' + formResult);
  
  // Test sequence addition  
  var sequenceResult = addToSequence(testEmail, testName, URGENT_FORECLOSURE_SEQUENCE);
  console.log('Final sequence result: ' + sequenceResult);
  
  return {
    email: testEmail,
    formResult: formResult,
    sequenceResult: sequenceResult
  };
}

// ============ VERIFY CREDENTIALS ============
function verifyConvertKitCredentials() {
  console.log('=== VERIFYING CONVERTKIT CREDENTIALS ===');
  console.log('API Key: ' + CONVERTKIT_API_KEY);
  console.log('API Secret: ' + CONVERTKIT_API_SECRET);
  console.log('Form ID: ' + CONVERTKIT_FORM_ID);
  console.log('Sequence ID: ' + URGENT_FORECLOSURE_SEQUENCE);
  
  // Test basic API connection
  try {
    var response = UrlFetchApp.fetch('https://api.convertkit.com/v3/account?api_secret=' + CONVERTKIT_API_SECRET);
    console.log('Account API Response: ' + response.getContentText());
  } catch (error) {
    console.log('Account API Error: ' + error.toString());
  }
}
// SIMPLE CONVERTKIT TEST - COPY THIS INTO GOOGLE APPS SCRIPT

function simpleConvertKitTest() {
  // Your working API details
  var FORM_ID = '8430004';
  var API_KEY = 'Hh9PtQFOyWkQN4SZ3w0iXA';
  var url = 'https://api.convertkit.com/v3/forms/' + FORM_ID + '/subscribe';
  
  var payload = {
    api_key: API_KEY,
    email: 'test' + Date.now() + '@example.com', // Unique email each time
    first_name: 'TestUser'
  };
  
  var options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  };
  
  try {
    console.log('Testing ConvertKit with email: ' + payload.email);
    var response = UrlFetchApp.fetch(url, options);
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

// SIMPLE FORM HANDLER - REPLACE YOUR doPost WITH THIS
function doPost(e) {
  try {
    console.log('Form submission received');
    
    // Parse form data
    var data = JSON.parse(e.postData.contents);
    console.log('Data received: ' + JSON.stringify(data));
    
    // Save to Google Sheets (your existing function)
    saveToGoogleSheets(data);
    console.log('Saved to Google Sheets');
    
    // Simple ConvertKit integration
    if (data.email) {
      console.log('Adding to ConvertKit: ' + data.email);
      var result = addToConvertKitSimple(data.email, data.name);
      console.log('ConvertKit result: ' + result);
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

function addToConvertKitSimple(email, name) {
  var FORM_ID = '8430004';
  var API_KEY = 'Hh9PtQFOyWkQN4SZ3w0iXA';
  var url = 'https://api.convertkit.com/v3/forms/' + FORM_ID + '/subscribe';
  
  var payload = {
    api_key: API_KEY,
    email: email,
    first_name: name ? name.split(' ')[0] : ''
  };
  
  try {
    var response = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      payload: JSON.stringify(payload)
    });
    
    console.log('ConvertKit Response Code: ' + response.getResponseCode());
    
    if (response.getResponseCode() === 200) {
      console.log('SUCCESS: Added to ConvertKit');
      return 'success';
    } else {
      console.log('FAILED: ' + response.getContentText());
      return 'failed';
    }
  } catch (error) {
    console.log('ConvertKit Error: ' + error.toString());
    return 'error';
  }
}
/**
 * Enhanced Google Apps Script for ConvertKit Integration
 * 
 * This script:
 * 1. Receives form submissions from your website
 * 2. Saves data to Google Sheets
 * 3. Automatically adds leads to ConvertKit with proper tags
 * 4. Triggers appropriate email sequences
 * 5. Sends notification alerts
 * 
 * Setup Instructions:
 * 1. Go to script.google.com
 * 2. Create new project
 * 3. Replace Code.gs with this content
 * 4. Add your ConvertKit API key below
 * 5. Create a Google Sheet and add its ID below
 * 6. Deploy as web app (Execute as: Me, Access: Anyone)
 */

// ============ CONFIGURATION ============
// SECURITY: API keys moved to Google Apps Script Properties
// Set these in your Google Apps Script: Project Settings > Script Properties
const CONVERTKIT_API_KEY = PropertiesService.getScriptProperties().getProperty('CONVERTKIT_API_KEY');
const CONVERTKIT_API_SECRET = PropertiesService.getScriptProperties().getProperty('CONVERTKIT_API_SECRET');
const GOOGLE_SHEET_ID = '1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU';
const NOTIFICATION_EMAIL = 'jumaanebey@gmail.com';

// ConvertKit Form IDs (create these in ConvertKit first)
const CONVERTKIT_FORMS = {
  'foreclosure_checklist': 'YOUR_FORM_ID', // For PDF downloads
  'cash_offer_request': 'YOUR_FORM_ID',    // For calculator submissions
  'contact_inquiry': 'YOUR_FORM_ID',       // For general contact
  'emergency_help': 'YOUR_FORM_ID'         // For urgent requests
};

// ============ MAIN FUNCTION ============
function doPost(e) {
  try {
    // Parse the incoming data
    const data = JSON.parse(e.postData.contents);
    console.log('Received data:', data);

    // Handle iPhone lead alerts (email-to-SMS)
    if (data.type === 'lead_alert' && data.to && data.to.includes('@txt.att.com')) {
      console.log('Processing iPhone lead alert');
      sendPhoneAlert(data);
      return ContentService
        .createTextOutput(JSON.stringify({success: true, type: 'phone_alert'}))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Save to Google Sheets
    saveToGoogleSheets(data);

    // Add to ConvertKit
    addToConvertKit(data);

    // Send notification if urgent
    if (isUrgentLead(data)) {
      sendUrgentNotification(data);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error processing form:', error);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false, 
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ============ GOOGLE SHEETS FUNCTIONS ============
function saveToGoogleSheets(data) {
  const sheet = SpreadsheetApp.openById(GOOGLE_SHEET_ID).getActiveSheet();
  
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
    data.property_address || '',
    data.desired_price || '',
    data.property_type || '',
    data.property_condition || '',
    data.timeline || '',
    data.foreclosure_status || '',
    data.best_time || ''
  ]);
  
  console.log('Data saved to Google Sheets');
}

// ============ CONVERTKIT FUNCTIONS ============
function addToConvertKit(data) {
  if (!data.email) {
    console.log('No email provided, skipping ConvertKit');
    return;
  }
  
  try {
    console.log('Starting ConvertKit integration for:', data.email);
    
    // Add subscriber to ConvertKit
    const subscriberId = addSubscriber(data);
    
    if (subscriberId) {
      console.log('Subscriber added successfully with ID:', subscriberId);
      
      // Add appropriate tags
      const tags = getTagsForLead(data);
      console.log('Adding tags:', tags);
      addTagsToSubscriber(subscriberId, tags);
      
      console.log('Successfully processed ConvertKit integration for:', data.email);
    } else {
      console.error('Failed to add subscriber to ConvertKit');
    }
    
  } catch (error) {
    console.error('ConvertKit integration error:', error.toString());
  }
}

function addSubscriber(data) {
  const url = 'https://api.convertkit.com/v3/subscribers';
  
  const payload = {
    api_key: CONVERTKIT_API_KEY,
    email: data.email,
    first_name: data.name ? data.name.split(' ')[0] : '',
    fields: {
      phone: data.phone || '',
      property_address: data.property_address || data.address || '',
      desired_price: data.desired_price || '',
      timeline: data.timeline || '',
      foreclosure_status: data.foreclosure_status || '',
      lead_source: data.type || 'website'
    }
  };
  
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  };
  
  try {
    console.log('Attempting to add subscriber with payload:', JSON.stringify(payload));
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log('ConvertKit Response Code:', responseCode);
    console.log('ConvertKit Response Text:', responseText);
    
    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      if (result.subscription && result.subscription.subscriber) {
        console.log('Successfully added subscriber:', result.subscription.subscriber.id);
        return result.subscription.subscriber.id;
      }
    }
    
    console.error('Failed to add subscriber. Response:', responseText);
    return null;
    
  } catch (error) {
    console.error('Error adding subscriber:', error.toString());
    return null;
  }
}

function addTagsToSubscriber(subscriberId, tags) {
  tags.forEach(tag => {
    try {
      const url = `https://api.convertkit.com/v3/tags`;
      
      const payload = {
        api_key: CONVERTKIT_API_KEY,
        tag: {
          name: tag,
          subscriber_id: subscriberId
        }
      };
      
      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        payload: JSON.stringify(payload)
      };
      
      UrlFetchApp.fetch(url, options);
      console.log(`Tagged subscriber ${subscriberId} with: ${tag}`);
      
    } catch (error) {
      console.error(`Error adding tag ${tag}:`, error);
    }
  });
}

function addToForm(email, formId) {
  const url = `https://api.convertkit.com/v3/forms/${formId}/subscribe`;
  
  const payload = {
    api_key: CONVERTKIT_API_KEY,
    email: email
  };
  
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  };
  
  UrlFetchApp.fetch(url, options);
  console.log(`Added ${email} to form ${formId}`);
}

// ============ HELPER FUNCTIONS ============
function getTagsForLead(data) {
  const tags = ['foreclosure-lead'];
  
  // Add source tag
  switch (data.type) {
    case 'exit_intent_popup':
      tags.push('source-exit-popup');
      break;
    case 'cash_offer_request':
      tags.push('source-calculator');
      break;
    case 'contact_form':
      tags.push('source-contact-form');
      break;
    case 'lead_magnet':
      tags.push('source-lead-magnet');
      break;
  }
  
  // Add timeline tag
  if (data.timeline) {
    tags.push(`timeline-${data.timeline}`);
  }
  
  // Add urgency tag
  if (isUrgentLead(data)) {
    tags.push('urgent-lead');
  }
  
  return tags;
}

function getFormForLeadType(type) {
  switch (type) {
    case 'exit_intent_popup':
    case 'lead_magnet':
      return CONVERTKIT_FORMS.foreclosure_checklist;
    case 'cash_offer_request':
      return CONVERTKIT_FORMS.cash_offer_request;
    case 'contact_form':
      return CONVERTKIT_FORMS.contact_inquiry;
    case 'emergency_help':
      return CONVERTKIT_FORMS.emergency_help;
    default:
      return CONVERTKIT_FORMS.contact_inquiry;
  }
}

function isUrgentLead(data) {
  return data.timeline === 'immediate' || 
         data.foreclosure_status === 'yes' ||
         data.type === 'emergency_help';
}

// ============ PHONE ALERT FUNCTIONS ============
function sendPhoneAlert(data) {
  try {
    // Extract phone number from AT&T email gateway format
    const phoneNumber = data.to.split('@')[0];

    console.log(`Sending iPhone alert to ${phoneNumber}: ${data.subject}`);

    // Send email to AT&T SMS gateway
    GmailApp.sendEmail(
      data.to,           // To: 9493284811@txt.att.com
      data.subject,      // Subject: 🚨 URGENT LEAD
      data.message       // Body: Lead details
    );

    console.log('iPhone alert sent successfully via email-to-SMS gateway');

    // Also send a copy to your main email as backup
    GmailApp.sendEmail(
      NOTIFICATION_EMAIL,
      `[BACKUP] ${data.subject}`,
      `iPhone Alert Sent:\n\n${data.message}\n\nOriginal sent to: ${data.to}`
    );

    return true;

  } catch (error) {
    console.error('Failed to send iPhone alert:', error);

    // If SMS gateway fails, still send regular email notification
    try {
      GmailApp.sendEmail(
        NOTIFICATION_EMAIL,
        `[FALLBACK] ${data.subject}`,
        `iPhone SMS alert failed, sending email backup:\n\n${data.message}\n\nError: ${error.toString()}`
      );
    } catch (emailError) {
      console.error('Fallback email also failed:', emailError);
    }

    return false;
  }
}

// ============ NOTIFICATION FUNCTIONS ============
function sendUrgentNotification(data) {
  const subject = `🚨 URGENT FORECLOSURE LEAD: ${data.name || 'New Lead'}`;
  
  const body = `
URGENT FORECLOSURE LEAD RECEIVED

Name: ${data.name || 'Not provided'}
Email: ${data.email || 'Not provided'}
Phone: ${data.phone || 'Not provided'}
Property: ${data.property_address || 'Not provided'}
Desired Price: ${data.desired_price ? '$' + Number(data.desired_price).toLocaleString() : 'Not provided'}
Timeline: ${data.timeline || 'Not provided'}
Foreclosure Status: ${data.foreclosure_status || 'Not provided'}
Lead Source: ${data.type || 'Unknown'}

ACTION REQUIRED: Contact this lead immediately!

Time received: ${new Date().toLocaleString()}
`;

  try {
    GmailApp.sendEmail(NOTIFICATION_EMAIL, subject, body);
    console.log('Urgent notification sent');
  } catch (error) {
    console.error('Failed to send notification:', error);
  }
}

// ============ TEST FUNCTIONS ============
function testConvertKitConnection() {
  const testData = {
    type: 'test',
    name: 'Test User',
    email: 'jumaanebey@gmail.com', // Use your real email for testing
    phone: '555-123-4567',
    timeline: 'immediate'
  };
  
  console.log('Testing ConvertKit connection...');
  console.log('API Key:', CONVERTKIT_API_KEY);
  console.log('API Secret:', CONVERTKIT_API_SECRET ? 'Present' : 'Missing');
  
  addToConvertKit(testData);
}

function testBasicConvertKitAPI() {
  // Test the simplest possible API call
  const url = 'https://api.convertkit.com/v3/subscribers';
  
  const payload = {
    api_key: CONVERTKIT_API_KEY,
    email: 'jumaanebey@gmail.com'
  };
  
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  };
  
  try {
    console.log('Testing basic ConvertKit API...');
    console.log('URL:', url);
    console.log('Payload:', JSON.stringify(payload));
    
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log('Response Code:', responseCode);
    console.log('Response Text:', responseText);
    
    return { code: responseCode, text: responseText };
    
  } catch (error) {
    console.error('API Test Error:', error.toString());
    return { error: error.toString() };
  }
}
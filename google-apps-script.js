/**
 * Google Apps Script for Contact Form Processing
 * Deploy this as a Web App to handle form submissions
 */

function doPost(e) {
  try {
    // Open your Google Sheet (replace with your sheet ID)
    const SHEET_ID = 'YOUR_GOOGLE_SHEET_ID_HERE';
    const sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    
    // Parse the incoming data
    const data = JSON.parse(e.postData.contents);
    
    // Validate required fields
    if (!data.name || !data.email || !data.phone) {
      return ContentService
        .createTextOutput(JSON.stringify({success: false, message: 'Missing required fields'}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Prepare row data
    const rowData = [
      new Date(),                    // Timestamp
      data.name,                     // Name
      data.email,                    // Email
      data.phone,                    // Phone
      data.address || '',            // Address
      data.situation || '',          // Situation
      'Website Form',                // Source
      'New'                         // Status
    ];
    
    // Add headers if sheet is empty
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, 8).setValues([[
        'Timestamp', 'Name', 'Email', 'Phone', 'Address', 'Situation', 'Source', 'Status'
      ]]);
    }
    
    // Add the data
    sheet.appendRow(rowData);
    
    // Send email notification
    sendEmailNotification(data);
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true, message: 'Form submitted successfully'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error processing form:', error);
    return ContentService
      .createTextOutput(JSON.stringify({success: false, message: 'Server error'}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function sendEmailNotification(data) {
  const EMAIL_ADDRESS = 'help@stopforeclosurefast.com'; // Replace with your email
  
  const subject = `🚨 New Foreclosure Lead: ${data.name}`;
  
  const body = `
New lead from Stop Foreclosure Fast website:

Name: ${data.name}
Email: ${data.email}
Phone: ${data.phone}
Property Address: ${data.address || 'Not provided'}

Situation:
${data.situation || 'Not provided'}

Submitted: ${new Date().toLocaleString()}

URGENT: Contact this lead within 15 minutes!
Call: ${data.phone}
Email: ${data.email}

Dashboard: https://docs.google.com/spreadsheets/d/YOUR_GOOGLE_SHEET_ID_HERE
  `;
  
  try {
    MailApp.sendEmail(EMAIL_ADDRESS, subject, body);
  } catch (error) {
    console.error('Error sending email:', error);
  }
}

function doGet(e) {
  return ContentService.createTextOutput('Contact form endpoint is working!');
}
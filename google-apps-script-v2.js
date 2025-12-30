/**
 * Google Apps Script v2 - With Twilio SMS Integration
 * My Foreclosure Solution
 *
 * SETUP:
 * 1. Go to script.google.com
 * 2. Create new project
 * 3. Paste this code
 * 4. Deploy as web app (Execute as: Me, Access: Anyone)
 * 5. Copy web app URL to your website form
 */

// ===== CONFIGURATION - UPDATE THESE =====
const CONFIG = {
  // Google Sheet (MUST match n8n Sheet ID)
  SPREADSHEET_ID: '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw',

  // Your email for notifications
  YOUR_EMAIL: 'help@myforeclosuresolution.com',

  // Twilio credentials - GET THESE FROM YOUR TWILIO DASHBOARD
  TWILIO_ACCOUNT_SID: 'YOUR_TWILIO_ACCOUNT_SID',
  TWILIO_AUTH_TOKEN: 'YOUR_TWILIO_AUTH_TOKEN',
  TWILIO_PHONE_NUMBER: 'YOUR_TWILIO_PHONE_NUMBER',

  // PDF Guide (optional)
  PDF_FILE_ID: '1YmRSqk8LJIEW97xgDaQEQ7-7gjcHRYuj'
};

/**
 * Main POST handler
 */
function doPost(e) {
  try {
    let data;

    if (e && e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      data = e.parameter;
    } else {
      throw new Error('No data received');
    }

    // Handle different request types
    if (data.type === 'sms_confirmation') {
      sendSMSConfirmation(data);
    } else if (data.type === 'lead_magnet') {
      logToSheet(data);
      sendPDFGuide(data);
      sendNotificationEmail(data);
    } else if (data.type === 'consultation') {
      logToSheet(data);
      sendSMSConfirmation(data);
      sendConsultationConfirmation(data);
      sendNotificationEmail(data);
    } else {
      logToSheet(data);
      sendNotificationEmail(data);
    }

    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    console.error('Error:', error);
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Log to Google Sheets
 */
function logToSheet(data) {
  const sheet = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID).getActiveSheet();

  // Add headers if first row
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      'Timestamp', 'Type', 'Name', 'Email', 'Phone', 'Property Address',
      'Urgency', 'Source', 'Status', 'Notes', 'Last Contact', 'Assigned To'
    ]);
  }

  const row = [
    new Date(),
    data.type || 'consultation',
    data.name || '',
    data.email || '',
    data.phone || '',
    data.property_address || '',
    data.urgency || '',
    data.source || 'website',
    'New',
    '',
    '',
    ''
  ];

  sheet.appendRow(row);
}

/**
 * Send SMS confirmation via Twilio
 */
function sendSMSConfirmation(data) {
  const phone = formatPhoneNumber(data.phone || data.to);
  if (!phone) return;

  const urgencyMessages = {
    'emergency': "🚨 URGENT: We see your sale is within 7 days. We're treating this as a priority case. Expect our call within 15 minutes!",
    'urgent': "⚠️ We received your request and understand time is limited. We'll call you within 30 minutes.",
    'soon': "📅 Thanks for reaching out! We'll call you within 30 minutes to discuss your options.",
    'exploring': "Thanks for contacting us! We'll call you within 30 minutes for a no-pressure consultation."
  };

  const urgencyText = urgencyMessages[data.urgency] || urgencyMessages['exploring'];

  const message = `Hi ${data.name || 'there'}! This is My Foreclosure Solution. ${urgencyText}

If you need immediate help, call us: (949) 565-5285

Reply STOP to opt out.`;

  sendTwilioSMS(phone, message);
}

/**
 * Send SMS via Twilio API
 */
function sendTwilioSMS(to, message) {
  const url = `https://api.twilio.com/2010-04-01/Accounts/${CONFIG.TWILIO_ACCOUNT_SID}/Messages.json`;

  const payload = {
    'To': to,
    'From': CONFIG.TWILIO_PHONE_NUMBER,
    'Body': message
  };

  const options = {
    'method': 'post',
    'headers': {
      'Authorization': 'Basic ' + Utilities.base64Encode(CONFIG.TWILIO_ACCOUNT_SID + ':' + CONFIG.TWILIO_AUTH_TOKEN)
    },
    'payload': payload,
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const result = JSON.parse(response.getContentText());
    console.log('SMS sent:', result.sid);
    return result;
  } catch (error) {
    console.error('SMS Error:', error);
    return null;
  }
}

/**
 * Format phone number for Twilio
 */
function formatPhoneNumber(phone) {
  if (!phone) return null;
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return '+1' + cleaned;
  } else if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return '+' + cleaned;
  }
  return null;
}

/**
 * Send consultation confirmation email
 */
function sendConsultationConfirmation(data) {
  const isEmergency = data.urgency === 'emergency';
  const subject = isEmergency
    ? `🚨 EMERGENCY REQUEST RECEIVED - ${data.name}`
    : `We received your request - ${data.name}`;

  const htmlBody = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: linear-gradient(135deg, #ea580c, #dc2626); color: white; padding: 30px; text-align: center;">
        <h1 style="margin: 0;">We're Here to Help</h1>
      </div>
      <div style="padding: 30px; background: white;">
        <p>Hi ${data.name},</p>
        <p><strong>${isEmergency ? "We see your situation is urgent. We're treating this as a priority case and will call you within 15 minutes." : "We received your request and will call you within 30 minutes."}</strong></p>

        ${isEmergency ? `
        <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #dc2626; margin-top: 0;">🚨 EMERGENCY PRIORITY</h3>
          <p>Can't wait? Call us now: <a href="tel:+1-949-565-5285" style="color: #dc2626; font-weight: bold;">(949) 565-5285</a></p>
        </div>
        ` : ''}

        <p><strong>While you wait:</strong></p>
        <ul>
          <li>Gather any foreclosure notices you've received</li>
          <li>Have your mortgage statement ready</li>
          <li>Don't stress - you took the right step by reaching out</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
          <a href="tel:+1-949-565-5285" style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">📞 Call Now: (949) 565-5285</a>
        </div>

        <p>You're not alone in this.</p>
        <p>Best regards,<br><strong>My Foreclosure Solution Team</strong><br>CA DRE #02076038 | NMLS #2033637</p>
      </div>
    </div>
  `;

  MailApp.sendEmail({
    to: data.email,
    subject: subject,
    htmlBody: htmlBody
  });
}

/**
 * Send notification email to you
 */
function sendNotificationEmail(data) {
  const isEmergency = data.urgency === 'emergency';
  const urgentFlag = isEmergency ? '🚨 EMERGENCY: ' : '';
  const subject = `${urgentFlag}New Lead - ${data.name} (${data.urgency || 'unknown'})`;

  const body = `
NEW LEAD RECEIVED
━━━━━━━━━━━━━━━━━━━━
Name: ${data.name}
Phone: ${data.phone}
Email: ${data.email}
Property: ${data.property_address || 'Not provided'}
Urgency: ${data.urgency || 'Not specified'}
Source: ${data.source || 'Website'}
Time: ${new Date().toLocaleString()}

${isEmergency ? '⚠️ EMERGENCY - CALL WITHIN 15 MINUTES!' : 'Follow up within 30 minutes.'}

Google Sheet: https://docs.google.com/spreadsheets/d/${CONFIG.SPREADSHEET_ID}
  `;

  MailApp.sendEmail({
    to: CONFIG.YOUR_EMAIL,
    subject: subject,
    body: body
  });
}

/**
 * Send PDF Guide (for lead magnet)
 */
function sendPDFGuide(data) {
  try {
    const pdfFile = DriveApp.getFileById(CONFIG.PDF_FILE_ID);

    MailApp.sendEmail({
      to: data.email,
      subject: `Your FREE Foreclosure Survival Guide - ${data.name}`,
      htmlBody: `<p>Hi ${data.name},</p><p>Your guide is attached!</p><p>Call us at (949) 565-5285 if you need immediate help.</p>`,
      attachments: [pdfFile.getBlob()]
    });
  } catch (error) {
    console.error('PDF send error:', error);
  }
}

/**
 * Test functions
 */
function testSMS() {
  sendTwilioSMS('+1YOURPHONE', 'Test from My Foreclosure Solution');
}

function testFullFlow() {
  const testData = {
    type: 'consultation',
    name: 'Test User',
    email: 'help@myforeclosuresolution.com',
    phone: '+1YOURPHONE',
    property_address: '123 Test St, LA, CA',
    urgency: 'urgent',
    source: 'test'
  };

  logToSheet(testData);
  sendSMSConfirmation(testData);
  console.log('Test complete!');
}

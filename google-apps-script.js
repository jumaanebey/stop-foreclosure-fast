/**
 * Enhanced Google Apps Script for Foreclosure Website
 * Handles form submissions AND automatic PDF email delivery
 *
 * Setup Instructions:
 * 1. Create new Google Apps Script project
 * 2. Replace Code.gs with this code
 * 3. Deploy as web app (Execute as: Me, Access: Anyone)
 * 4. Copy the web app URL to your forms
 * 5. Upload your PDF guide to Google Drive
 * 6. Replace PDF_FILE_ID with your actual file ID
 */

// Configuration - UPDATE THESE VALUES
const SPREADSHEET_ID = '1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw';
const PDF_FILE_ID = '1YmRSqk8LJIEW97xgDaQEQ7-7gjcHRYuj';
const YOUR_EMAIL = 'help@myforeclosuresolutions.com';

/**
 * Main function that handles all POST requests
 */
function doPost(e) {
  try {
    console.log('Form submission received');

    // Check if e exists at all
    if (typeof e === 'undefined') {
      console.log('ERROR: e is undefined');
      return ContentService
        .createTextOutput(JSON.stringify({success: false, error: 'Event parameter is undefined'}))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Try to safely log e
    try {
      console.log('Event object type:', typeof e);
      console.log('Event keys:', e ? Object.keys(e).join(', ') : 'none');
    } catch (logError) {
      console.log('Could not log event object:', logError);
    }

    let data;

    // Handle different request formats
    if (e && e.postData && e.postData.contents) {
      console.log('Using postData.contents');
      data = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      console.log('Using parameter');
      data = e.parameter;
    } else if (e && e.parameters) {
      console.log('Using parameters');
      data = {};
      for (let key in e.parameters) {
        data[key] = e.parameters[key][0];
      }
    } else {
      console.log('No recognized data format');
      console.log('Has postData?', !!(e && e.postData));
      console.log('Has parameter?', !!(e && e.parameter));
      console.log('Has parameters?', !!(e && e.parameters));
      throw new Error('No data received - unknown format');
    }

    console.log('Successfully parsed data');

    // Log the submission to Google Sheets
    logToSheet(data);

    // Send automatic email based on submission type
    if (data.type === 'lead_magnet') {
      sendPDFGuide(data);
    } else if (data.type === 'consultation') {
      sendConsultationConfirmation(data);
    }

    // Send notification to you
    sendNotificationEmail(data);

    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    console.error('Error in doPost:', error.toString());
    try {
      console.error('Error stack:', error.stack);
    } catch (stackError) {
      console.error('Could not log stack');
    }
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Log submission to Google Sheets
 */
function logToSheet(data) {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getActiveSheet();

  // Add headers if this is the first row
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      'Timestamp', 'Type', 'Name', 'Email', 'Phone', 'Property Address',
      'Situation', 'Timeline', 'Preferred Contact', 'Source', 'Status'
    ]);
  }

  // Add the new submission
  const row = [
    new Date(),
    data.type || 'unknown',
    data.name || '',
    data.email || '',
    data.phone || '',
    data.property_address || '',
    data.situation || '',
    data.timeline || '',
    data.preferred_contact || '',
    data.source || 'website',
    'New Lead'
  ];

  sheet.appendRow(row);
}

/**
 * Send PDF Guide for lead magnet submissions
 */
function sendPDFGuide(data) {
  const pdfFile = DriveApp.getFileById(PDF_FILE_ID);

  const subject = `Your FREE 7-Day Foreclosure Survival Guide - ${data.name}`;

  const htmlBody = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: linear-gradient(135deg, #ea580c, #dc2626); color: white; padding: 30px; text-align: center;">
        <h1 style="margin: 0; font-size: 28px;">Your FREE Guide is Here!</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Stop Your Foreclosure in 7 Days or Less</p>
      </div>

      <div style="padding: 30px; background: white;">
        <p>Hi ${data.name},</p>

        <p><strong>Thank you for downloading our 7-Day Foreclosure Survival Guide!</strong></p>

        <p>You now have access to the same strategies we've used to help over 500 California families save their homes.</p>

        <div style="background: #fef3e2; padding: 20px; border-left: 4px solid #ea580c; margin: 20px 0;">
          <h3 style="color: #7c2d12; margin-top: 0;">⏰ If your situation is urgent:</h3>
          <p style="margin-bottom: 0;"><strong>Call us immediately at (949) 565-5285</strong></p>
          <p>We've stopped foreclosures the day before auction. Don't wait.</p>
        </div>

        <h3>What's in your guide:</h3>
        <ul>
          <li>📋 Day-by-day action plan to stop foreclosure</li>
          <li>📞 Exact scripts for calling your lender</li>
          <li>⚖️ Your legal rights in California</li>
          <li>💰 How to keep your home's equity</li>
          <li>❌ 7 costly mistakes to avoid</li>
          <li>✅ Success stories from real families</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
          <a href="tel:+1-949-565-5285" style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
            📞 Need Help? Call (949) 565-5285
          </a>
        </div>

        <p><strong>Remember:</strong> Every day matters in foreclosure. Even if your situation seems hopeless, we've seen solutions work at the last minute.</p>

        <p>You're not alone in this.</p>

        <p>Best regards,<br>
        <strong>My Foreclosure Solution Team</strong><br>
        CA DRE #02076038 | NMLS #2033637<br>
        (949) 565-5285</p>
      </div>

      <div style="background: #f9fafb; padding: 20px; text-align: center; font-size: 14px; color: #6b7280;">
        <p>This email was sent because you requested our free foreclosure guide.</p>
        <p>My Foreclosure Solution • Licensed CA Real Estate Professional</p>
      </div>
    </div>
  `;

  const textBody = `
Hi ${data.name},

Thank you for downloading our 7-Day Foreclosure Survival Guide!

You now have access to the same strategies we've used to help over 500 California families save their homes.

⏰ URGENT SITUATIONS: If your sale is within 7 days, call us immediately at (949) 565-5285. We've stopped foreclosures the day before auction.

What's in your guide:
• Day-by-day action plan to stop foreclosure
• Exact scripts for calling your lender
• Your legal rights in California
• How to keep your home's equity
• 7 costly mistakes to avoid
• Success stories from real families

Need personal help? Call (949) 565-5285 for a free consultation.

Remember: Every day matters in foreclosure. You're not alone in this.

Best regards,
My Foreclosure Solution Team
CA DRE #02076038 | NMLS #2033637
(949) 565-5285
  `;

  MailApp.sendEmail({
    to: data.email,
    subject: subject,
    htmlBody: htmlBody,
    body: textBody,
    attachments: [pdfFile.getBlob()]
  });
}

/**
 * Send consultation confirmation email
 */
function sendConsultationConfirmation(data) {
  const subject = `We received your request - ${data.name}`;

  const htmlBody = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: linear-gradient(135deg, #ea580c, #dc2626); color: white; padding: 30px; text-align: center;">
        <h1 style="margin: 0; font-size: 28px;">We're Here to Help</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Your consultation request received</p>
      </div>

      <div style="padding: 30px; background: white;">
        <p>Hi ${data.name},</p>

        <p><strong>We received your request for help, and we'll call you within 30 minutes.</strong></p>

        ${data.timeline === 'emergency' ? `
        <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #dc2626; margin-top: 0;">🚨 EMERGENCY SITUATION DETECTED</h3>
          <p style="margin-bottom: 0;"><strong>We're treating your case as urgent priority.</strong></p>
          <p>Expect our call within 15 minutes, or call us immediately at (949) 565-5285.</p>
        </div>
        ` : ''}

        <h3>What happens next:</h3>
        <ol>
          <li><strong>We'll call you</strong> within 30 minutes for a private consultation</li>
          <li><strong>We'll review</strong> your specific situation and all available options</li>
          <li><strong>We'll create</strong> an action plan tailored to your needs</li>
          <li><strong>We'll start immediately</strong> if you decide to work with us</li>
        </ol>

        <div style="background: #fef3e2; padding: 20px; border-left: 4px solid #ea580c; margin: 20px 0;">
          <h3 style="color: #7c2d12; margin-top: 0;">While you wait:</h3>
          <p>• Gather any foreclosure notices you've received</p>
          <p>• Have your mortgage statement ready</p>
          <p>• Don't stress - you took the right step by reaching out</p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
          <a href="tel:+1-949-565-5285" style="background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
            📞 Can't Wait? Call (949) 565-5285
          </a>
        </div>

        <p>You're not alone in this. We're here to help.</p>

        <p>Best regards,<br>
        <strong>My Foreclosure Solution Team</strong><br>
        CA DRE #02076038 | NMLS #2033637</p>
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
 * Send notification email to you about new leads
 */
function sendNotificationEmail(data) {
  const urgentFlag = data.timeline === 'emergency' ? '🚨 EMERGENCY: ' : '';
  const subject = `${urgentFlag}New ${data.type} submission - ${data.name}`;

  const leadDetails = `
New Lead Details:
━━━━━━━━━━━━━━━━━━━━
Type: ${data.type}
Name: ${data.name}
Email: ${data.email}
Phone: ${data.phone || 'Not provided'}
Property: ${data.property_address || 'Not provided'}
Situation: ${data.situation || 'Not provided'}
Timeline: ${data.timeline || 'Not provided'}
Preferred Contact: ${data.preferred_contact || 'Not provided'}
Source: ${data.source || 'Website'}
Timestamp: ${new Date().toLocaleString()}

${data.timeline === 'emergency' ? '⚠️ URGENT: Contact immediately!' : 'Follow up within 30 minutes.'}
  `;

  MailApp.sendEmail({
    to: YOUR_EMAIL,
    subject: subject,
    body: leadDetails
  });
}

/**
 * Test function - Check if PDF is accessible
 */
function testPDFAccess() {
  try {
    const pdfFile = DriveApp.getFileById(PDF_FILE_ID);
    console.log('PDF file found:', pdfFile.getName());
    console.log('PDF file size:', pdfFile.getSize());
    return true;
  } catch (error) {
    console.error('Cannot access PDF:', error.toString());
    return false;
  }
}

/**
 * Test function - Tests PDF email delivery
 */
function testEmailDelivery() {
  try {
    const testData = {
      type: 'lead_magnet',
      name: 'Test User',
      email: 'help@myforeclosuresolution.com',
      source: 'test'
    };

    console.log('Sending PDF email with data:', JSON.stringify(testData));

    sendPDFGuide(testData);
    sendNotificationEmail(testData);

    console.log('Test PDF email sent successfully to help@myforeclosuresolution.com');
  } catch (error) {
    console.error('Error in testEmailDelivery:', error.toString());
    console.error('Stack:', error.stack);
  }
}
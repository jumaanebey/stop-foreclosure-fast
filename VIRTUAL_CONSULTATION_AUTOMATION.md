# Virtual Consultation Booking Automation Setup

## Google Sheets Lead Notification System

### 1. Google Sheets Script Setup
**Open your lead capture Google Sheet → Extensions → Apps Script**

```javascript
function onFormSubmit(e) {
  // Get the submitted data
  const sheet = e.source.getActiveSheet();
  const row = e.range.getRow();
  const data = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Extract lead information
  const timestamp = data[0];
  const name = data[1];
  const email = data[2];
  const phone = data[3];
  const county = data[4];
  const urgency = data[5];
  const device = data[6];
  const propertyAddress = data[7];
  const situation = data[8];
  
  // Send immediate notification email
  sendLeadNotification(name, email, phone, county, urgency, device, timestamp);
  
  // Send auto-responder to client
  sendClientAutoResponder(name, email, phone, urgency, device);
  
  // Create calendar event if urgent
  if (urgency === 'immediate' || urgency === 'urgent') {
    createUrgentCalendarEvent(name, phone, email, county);
  }
}

function sendLeadNotification(name, email, phone, county, urgency, device, timestamp) {
  const subject = `🚨 NEW VIRTUAL CONSULTATION LEAD - ${urgency.toUpperCase()} - ${name}`;
  
  const body = `
NEW VIRTUAL CONSULTATION REQUEST

URGENCY LEVEL: ${urgency.toUpperCase()}
TIME SUBMITTED: ${timestamp}

CLIENT INFORMATION:
Name: ${name}
Email: ${email}
Phone: ${phone}
County: ${county}
Device Preference: ${device}

REQUIRED RESPONSE TIME:
- Immediate/Urgent: Call within 2 hours
- Soon: Call within 4 hours  
- Exploring: Call within 24 hours
- Planning: Call within 48 hours

NEXT STEPS:
1. Call client at ${phone}
2. Send virtual consultation link
3. Provide DRE disclosure document
4. Schedule consultation appointment
5. Update CRM with contact details

CLIENT PORTAL: https://docs.google.com/spreadsheets/d/[your_sheet_id]
`;

  MailApp.sendEmail({
    to: 'help@myforeclosuresolution.com',
    subject: subject,
    body: body
  });
  
  // Send SMS notification for urgent leads
  if (urgency === 'immediate' || urgency === 'urgent') {
    sendSMSAlert(name, phone, county);
  }
}

function sendClientAutoResponder(name, email, phone, urgency, device) {
  const subject = 'Virtual Consultation Request Confirmed - California Foreclosure Help';
  
  const responseTime = {
    'immediate': 'within 1 hour',
    'urgent': 'within 2 hours', 
    'soon': 'within 4 hours',
    'exploring': 'within 24 hours',
    'planning': 'within 48 hours'
  };
  
  const body = `
Hi ${name},

Thank you for requesting a virtual foreclosure consultation. Your request has been received and confirmed.

YOUR REQUEST DETAILS:
- Urgency Level: ${urgency}
- Device Preference: ${device}
- Expected Response: ${responseTime[urgency] || 'within 24 hours'}

WHAT HAPPENS NEXT:

STEP 1: We'll call you at ${phone} ${responseTime[urgency] || 'within 24 hours'}
STEP 2: We'll email you a secure meeting link and preparation checklist
STEP 3: We'll conduct your 60-90 minute virtual consultation
STEP 4: You'll receive a written action plan with specific next steps

MEANWHILE, HERE'S IMMEDIATE HELP:

📋 Emergency Foreclosure Checklist: https://myforeclosuresolution.com/downloads/emergency-checklist
📞 If situation becomes urgent before our call, text "URGENT" to (949) 328-4811
🔒 Technology Test Link: We'll send this before your consultation

ABOUT OUR VIRTUAL CONSULTATIONS:

✅ No travel time - we can often schedule same-day help
✅ Secure document sharing - safer than physical papers  
✅ Session recording available - better than handwritten notes
✅ Available evenings/weekends - fits your schedule
✅ Licensed CA professionals (DRE #02076038)

We understand foreclosure is stressful. Our virtual consultation process is designed to be convenient, secure, and comprehensive - helping you understand all your options without adding the burden of travel.

We serve all 58 California counties virtually. Distance has never stopped us from helping a homeowner, and it won't stop us from helping you.

Talk to you ${responseTime[urgency] || 'soon'},

[Your Name]
Licensed California Real Estate Professional  
DRE License #02076038
My Foreclosure Solution
📞 (949) 328-4811
📧 help@myforeclosuresolution.com

P.S. Your information is 100% confidential and secure. We use bank-level encryption for all virtual consultations.
`;

  MailApp.sendEmail({
    to: email,
    subject: subject,
    body: body
  });
}

function createUrgentCalendarEvent(name, phone, email, county) {
  const calendar = CalendarApp.getDefaultCalendar();
  const now = new Date();
  const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  
  const event = calendar.createEvent(
    `URGENT: Virtual Consultation - ${name} (${county} County)`,
    tomorrow,
    new Date(tomorrow.getTime() + 90 * 60 * 1000), // 90 minute consultation
    {
      description: `
URGENT VIRTUAL FORECLOSURE CONSULTATION

Client: ${name}
Phone: ${phone}  
Email: ${email}
County: ${county}

PRE-CONSULTATION CHECKLIST:
□ Send DRE disclosure document
□ Send secure meeting link
□ Send preparation checklist
□ Confirm device compatibility
□ Review client property/situation

CONSULTATION AGENDA:
□ Introduction and credential verification
□ Situation analysis and timeline review
□ Document review (foreclosure notices, etc.)
□ California foreclosure law application
□ All available options presentation
□ Property valuation estimate
□ Action plan development
□ Next steps and follow-up scheduling

REQUIRED MATERIALS:
- DRE License disclosure
- Virtual consultation security info
- California foreclosure timeline
- Property valuation tools
- Action plan template
`,
      location: 'Virtual Consultation (Secure Video Call)'
    }
  );
}
```

### 2. Trigger Setup
**In Apps Script:**
1. Click "Triggers" (clock icon)
2. Add Trigger:
   - Function: `onFormSubmit`
   - Event Source: From spreadsheet
   - Event Type: On form submit
3. Save and authorize

### 3. SMS Alert Integration (Optional)
**Using Twilio API for urgent leads:**

```javascript
function sendSMSAlert(clientName, clientPhone, county) {
  const twilioUrl = 'https://api.twilio.com/2010-04-01/Accounts/[ACCOUNT_SID]/Messages.json';
  
  const payload = {
    'From': '+1234567890', // Your Twilio number
    'To': '+19493284811',   // Your business phone
    'Body': `🚨 URGENT Virtual Consultation Lead: ${clientName} in ${county} County. Call ${clientPhone} within 2 hours. Check email for details.`
  };
  
  const options = {
    'method': 'POST',
    'payload': payload,
    'headers': {
      'Authorization': 'Basic ' + Utilities.base64Encode('[ACCOUNT_SID]:[AUTH_TOKEN]')
    }
  };
  
  UrlFetchApp.fetch(twilioUrl, options);
}
```

## Calendar Integration Setup

### Google Calendar Virtual Consultation Template
**Create recurring appointment slots:**

**Template Event:**
- **Title:** "Virtual Consultation Available"
- **Duration:** 90 minutes
- **Recurring:** Daily, M-F 9am, 1pm, 5pm; Sat 10am, 2pm
- **Location:** "Virtual - Secure Video Call"
- **Description:** "Available slot for virtual foreclosure consultation"

### Calendly Integration (Alternative)
**Set up at calendly.com:**

1. **Event Type:** "Free Virtual Foreclosure Consultation"
2. **Duration:** 90 minutes
3. **Availability:** M-F 9am-7pm, Sat 10am-4pm
4. **Location:** Virtual (Google Meet/Zoom)
5. **Questions to Ask:**
   - Full name
   - Phone number
   - Email address
   - Property county
   - Urgency level
   - Device preference
   - Brief situation description

## Lead Tracking Dashboard

### Google Sheets Lead Tracker Template
**Columns:**
- Timestamp
- Name
- Email  
- Phone
- County
- Urgency
- Device
- Status (New/Contacted/Scheduled/Completed)
- Consultation Date
- Outcome
- Follow-up Required
- Source (Website/Thumbtack/Bark/etc.)

### Automated Status Updates
```javascript
function updateLeadStatus(row, status) {
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.getRange(row, 9).setValue(status); // Status column
  sheet.getRange(row, 13).setValue(new Date()); // Last updated
}
```

## Integration Testing Checklist

### Test Scenarios:
1. **Form Submission Test**
   - Submit test lead through website form
   - Verify email notification received
   - Check auto-responder sent to test email
   - Confirm lead appears in tracking sheet

2. **Urgent Lead Test**
   - Submit with "immediate" urgency
   - Verify SMS alert sent (if configured)
   - Check calendar event created
   - Confirm priority handling

3. **Multi-device Test**
   - Test form on desktop, tablet, mobile
   - Verify all device types trigger automation
   - Check formatting in email notifications

4. **Error Handling Test**
   - Submit incomplete forms
   - Test with invalid email/phone formats
   - Verify graceful error handling

This automation ensures no lead is missed and provides immediate, professional response to every virtual consultation request.
# Lead Tracking Dashboard Setup

## Google Sheets Lead Management System

### Master Lead Tracking Sheet Structure

```
Column A: Timestamp
Column B: Source (Website/Thumbtack/Bark/Fiverr/GMB/Referral)
Column C: Lead ID (Auto-generated)
Column D: Full Name
Column E: Email Address
Column F: Phone Number  
Column G: Property County
Column H: Property Address (if provided)
Column I: Urgency Level (Immediate/Urgent/Soon/Exploring/Planning)
Column J: Device Preference (Computer/Tablet/Phone/No Preference)
Column K: Situation Description
Column L: Lead Status (New/Contacted/Qualified/Scheduled/Completed/Lost)
Column M: First Contact Date
Column N: Consultation Scheduled Date
Column O: Consultation Completed Date
Column P: Outcome (Consultation Only/Cash Offer/Loan Mod/Referral/No Action)
Column Q: Revenue Generated
Column R: Follow-up Required (Yes/No)
Column S: Next Follow-up Date
Column T: Assigned Agent
Column U: Notes
Column V: Lead Score (1-100)
Column W: Conversion Probability (High/Medium/Low)
Column X: Last Contact Date
Column Y: Contact Attempts
Column Z: Marketing Campaign (if applicable)
```

### Lead Scoring Formula
```
=IF(I2="immediate",100,IF(I2="urgent",80,IF(I2="soon",60,IF(I2="exploring",40,20))))
```

### Automated Status Updates
```javascript
// Google Apps Script for status automation
function updateLeadStatus() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    const timestamp = data[i][0];
    const status = data[i][11];
    const urgency = data[i][8];
    
    // Auto-update overdue leads
    if (status === 'New' && isOverdue(timestamp, urgency)) {
      sheet.getRange(i + 1, 12).setValue('OVERDUE - CONTACT IMMEDIATELY');
      sheet.getRange(i + 1, 12).setBackground('#ff0000');
    }
  }
}

function isOverdue(timestamp, urgency) {
  const now = new Date();
  const submitted = new Date(timestamp);
  const hoursDiff = (now - submitted) / (1000 * 60 * 60);
  
  const responseTime = {
    'immediate': 1,
    'urgent': 2,
    'soon': 4,
    'exploring': 24,
    'planning': 48
  };
  
  return hoursDiff > (responseTime[urgency] || 24);
}
```

## Lead Source Performance Dashboard

### Source Tracking Sheet
```
Column A: Lead Source
Column B: Total Leads
Column C: Qualified Leads
Column D: Consultations Scheduled
Column E: Consultations Completed
Column F: Conversion Rate
Column G: Average Lead Score
Column H: Total Revenue
Column I: Cost Per Lead
Column J: ROI
Column K: Best Performing Time
Column L: Geographic Distribution
```

### Performance Formulas
```
// Conversion Rate
=C2/B2*100

// ROI Calculation  
=H2/I2*100

// Lead Quality Score
=G2/COUNT(B:B)
```

## Real-Time Notification System

### Slack Integration (Optional)
```javascript
function sendSlackNotification(leadData) {
  const webhookUrl = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK';
  
  const message = {
    'text': `🚨 NEW VIRTUAL CONSULTATION LEAD`,
    'attachments': [{
      'color': leadData.urgency === 'immediate' ? 'danger' : 'warning',
      'fields': [
        {'title': 'Name', 'value': leadData.name, 'short': true},
        {'title': 'County', 'value': leadData.county, 'short': true},
        {'title': 'Urgency', 'value': leadData.urgency, 'short': true},
        {'title': 'Phone', 'value': leadData.phone, 'short': true},
        {'title': 'Source', 'value': leadData.source, 'short': true},
        {'title': 'Device', 'value': leadData.device, 'short': true}
      ]
    }]
  };
  
  UrlFetchApp.fetch(webhookUrl, {
    'method': 'POST',
    'contentType': 'application/json',
    'payload': JSON.stringify(message)
  });
}
```

### Email Digest Setup
```javascript
function sendDailyLeadDigest() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const today = new Date();
  const todayLeads = sheet.getDataRange().getValues().filter(row => {
    const leadDate = new Date(row[0]);
    return leadDate.toDateString() === today.toDateString();
  });
  
  const subject = `Daily Lead Report - ${today.toDateString()} - ${todayLeads.length} New Leads`;
  
  let body = `DAILY VIRTUAL CONSULTATION LEAD REPORT\n\n`;
  body += `DATE: ${today.toDateString()}\n`;
  body += `NEW LEADS TODAY: ${todayLeads.length}\n\n`;
  
  body += `URGENCY BREAKDOWN:\n`;
  const urgencyCount = {};
  todayLeads.forEach(lead => {
    urgencyCount[lead[8]] = (urgencyCount[lead[8]] || 0) + 1;
  });
  
  Object.keys(urgencyCount).forEach(urgency => {
    body += `- ${urgency}: ${urgencyCount[urgency]}\n`;
  });
  
  body += `\nTOP PERFORMING SOURCES TODAY:\n`;
  const sourceCount = {};
  todayLeads.forEach(lead => {
    sourceCount[lead[1]] = (sourceCount[lead[1]] || 0) + 1;
  });
  
  Object.keys(sourceCount).forEach(source => {
    body += `- ${source}: ${sourceCount[source]}\n`;
  });
  
  MailApp.sendEmail({
    to: 'help@myforeclosuresolution.com',
    subject: subject,
    body: body
  });
}
```

## Lead Qualification Automation

### Auto-Qualification Scoring
```javascript
function calculateLeadScore(leadData) {
  let score = 0;
  
  // Urgency scoring
  const urgencyScores = {
    'immediate': 50,
    'urgent': 40,
    'soon': 30,
    'exploring': 20,
    'planning': 10
  };
  score += urgencyScores[leadData.urgency] || 0;
  
  // County scoring (high-value markets)
  const countyScores = {
    'Los Angeles': 20,
    'Orange': 20,
    'San Diego': 15,
    'Santa Clara': 15,
    'San Francisco': 15
  };
  score += countyScores[leadData.county] || 10;
  
  // Source scoring
  const sourceScores = {
    'Website': 20,
    'Referral': 30,
    'Thumbtack': 15,
    'Bark': 15,
    'Google': 25
  };
  score += sourceScores[leadData.source] || 10;
  
  // Time of day scoring (business hours = higher score)
  const hour = new Date(leadData.timestamp).getHours();
  if (hour >= 9 && hour <= 17) {
    score += 10;
  }
  
  return Math.min(score, 100);
}
```

## Conversion Tracking Integration

### Google Analytics Events
```javascript
function trackLeadConversion(leadData, stage) {
  const gaTrackingId = 'G-ZC3FHFTPN2';
  
  const eventData = {
    'event_name': 'lead_progression',
    'event_category': 'virtual_consultation',
    'event_label': stage,
    'lead_source': leadData.source,
    'lead_urgency': leadData.urgency,
    'lead_county': leadData.county,
    'lead_score': leadData.score
  };
  
  // Send to Google Analytics via Measurement Protocol
  const payload = new URLSearchParams(eventData).toString();
  UrlFetchApp.fetch(`https://www.google-analytics.com/collect?${payload}`);
}
```

## Mobile Dashboard Access

### Google Sheets Mobile App Setup
1. **Install Google Sheets app**
2. **Create "Virtual Consultation Leads" bookmark**
3. **Set up notifications for urgent leads**
4. **Configure offline access for lead data**

### Quick Action Buttons
**Add these to your sheet for mobile use:**
- "Mark as Contacted" button
- "Schedule Consultation" button  
- "Mark as Completed" button
- "Add Notes" button

## Weekly Performance Reports

### Automated Weekly Summary
```javascript
function generateWeeklyReport() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
  
  const weeklyLeads = sheet.getDataRange().getValues().filter(row => {
    return new Date(row[0]) >= oneWeekAgo;
  });
  
  const report = {
    totalLeads: weeklyLeads.length,
    urgentLeads: weeklyLeads.filter(l => l[8] === 'urgent' || l[8] === 'immediate').length,
    consultationsScheduled: weeklyLeads.filter(l => l[11] === 'Scheduled').length,
    consultationsCompleted: weeklyLeads.filter(l => l[11] === 'Completed').length,
    topSource: getMostCommonValue(weeklyLeads.map(l => l[1])),
    topCounty: getMostCommonValue(weeklyLeads.map(l => l[6])),
    averageScore: weeklyLeads.reduce((sum, l) => sum + (l[21] || 0), 0) / weeklyLeads.length
  };
  
  // Email the report
  sendWeeklyReport(report);
}
```

This comprehensive lead tracking system ensures no opportunity is missed and provides clear visibility into your virtual consultation business performance.
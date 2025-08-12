# Stop Foreclosure Fast - Pre-Foreclosure Marketing System

Complete sales funnel website and lead processing system for pre-foreclosure homeowner marketing.

## 🏗️ System Overview

- **Website**: Modern sales funnel hosted on GitHub Pages
- **Lead Processing**: Python system for daily Retran.com data processing
- **Marketing Automation**: Syncs to Mailchimp, Twilio, Google Ads, Facebook Ads
- **Lead Enrichment**: Adds emails via Hunter.io and Apollo.io APIs

## 📁 Directory Structure

```
stop-foreclosure-fast/
├── index.html              # Main landing page
├── contact-form.html        # Form processing page
├── thank-you.html          # Thank you page
├── css/
│   └── styles.css          # All styling
├── js/
│   └── script.js           # Form handling & analytics
├── images/
│   └── placeholder.jpg     # Image assets
├── lead_processor.py       # Main Python processing script
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── setup/                # Setup documentation
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Deploy Website to GitHub Pages

1. **Create GitHub Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/stop-foreclosure-fast.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Click "Settings" tab
   - Scroll to "Pages" section
   - Source: "Deploy from a branch"
   - Branch: "main" / root
   - Click "Save"

3. **Configure Analytics**:
   - Replace `GA_MEASUREMENT_ID` with your Google Analytics 4 ID
   - Replace `YOUR_PIXEL_ID` with your Facebook Pixel ID

### 2. Setup Lead Processing System

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Test the System**:
   ```bash
   python lead_processor.py
   ```

### 3. Schedule Daily Processing

**Linux/Mac (Cron)**:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * /usr/bin/python3 /path/to/lead_processor.py /path/to/retran_download.csv
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\lead_processor.py C:\path\to\retran_download.csv`

## 🔧 API Setup Instructions

### Google Analytics Setup

1. **Create GA4 Property**:
   - Go to [Google Analytics](https://analytics.google.com)
   - Create new property
   - Copy Measurement ID (format: G-XXXXXXXXXX)

2. **Update Website**:
   - Replace `GA_MEASUREMENT_ID` in index.html and thank-you.html

### Facebook Pixel Setup

1. **Create Facebook Pixel**:
   - Go to [Facebook Events Manager](https://business.facebook.com/events_manager)
   - Create new pixel
   - Copy Pixel ID

2. **Update Website**:
   - Replace `YOUR_PIXEL_ID` in all HTML files

### Google Sheets Contact Form (Alternative)

1. **Create Google Apps Script**:
   ```javascript
   function doPost(e) {
     const sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getActiveSheet();
     const data = JSON.parse(e.postData.contents);
     
     sheet.appendRow([
       new Date(),
       data.name,
       data.email,
       data.phone,
       data.address,
       data.situation
     ]);
     
     return ContentService.createTextOutput('Success');
   }
   ```

2. **Deploy as Web App**:
   - Deploy → New deployment
   - Type: Web app
   - Execute as: Me
   - Access: Anyone
   - Copy Web App URL

3. **Update script.js**:
   - Replace `YOUR_SCRIPT_ID` with your Web App URL

### Hunter.io API Setup

1. **Sign up**: [Hunter.io](https://hunter.io/api)
2. **Get API Key**: Dashboard → API → Your API Key
3. **Add to .env**: `HUNTER_API_KEY=your_key_here`

### Apollo.io API Setup

1. **Sign up**: [Apollo.io](https://developer.apollo.io/)
2. **Get API Key**: Settings → Integrations → API
3. **Add to .env**: `APOLLO_API_KEY=your_key_here`

### Mailchimp API Setup

1. **Get API Key**:
   - Mailchimp Account → Extras → API Keys
   - Create new API key

2. **Get List ID**:
   - Audience → Settings → Unique id for audience

3. **Get Server**:
   - From API key (us1, us2, etc.)

4. **Add to .env**:
   ```env
   MAILCHIMP_API_KEY=your_key_here
   MAILCHIMP_SERVER=us1
   MAILCHIMP_LIST_ID=your_list_id_here
   ```

### Twilio SMS Setup

1. **Create Twilio Account**: [Twilio.com](https://twilio.com)
2. **Get Credentials**:
   - Account SID
   - Auth Token
   - Phone Number

3. **Add to .env**:
   ```env
   TWILIO_ACCOUNT_SID=your_sid_here
   TWILIO_AUTH_TOKEN=your_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Google Ads API Setup

1. **Enable Google Ads API**:
   - [Google Cloud Console](https://console.cloud.google.com)
   - Enable Google Ads API

2. **Create OAuth Credentials**:
   - APIs & Services → Credentials
   - Create OAuth 2.0 client ID

3. **Get Developer Token**:
   - Google Ads Account → Tools → API Center
   - Apply for developer token

4. **Generate Refresh Token**:
   ```bash
   python -c "
   from google_auth_oauthlib.flow import InstalledAppFlow
   flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', ['https://www.googleapis.com/auth/adwords'])
   credentials = flow.run_local_server()
   print(f'Refresh token: {credentials.refresh_token}')
   "
   ```

### Facebook Ads API Setup

1. **Create Facebook App**:
   - [Facebook Developers](https://developers.facebook.com)
   - Create new app
   - Add Marketing API

2. **Get Access Token**:
   - Tools → Graph API Explorer
   - Generate User Access Token
   - Add permissions: `ads_management`, `ads_read`

3. **Get Ad Account ID**:
   - Facebook Ads Manager → Account Settings
   - Copy Account ID (format: act_XXXXXXXXXX)

## 📋 Daily Workflow

### Manual Process

1. **Download Retran.com Data**:
   - Login to Retran.com
   - Download daily CSV/XLS file

2. **Process Leads**:
   ```bash
   python lead_processor.py /path/to/retran_download.csv
   ```

3. **Verify Sync**:
   - Check Mailchimp audience
   - Check Google Ads audience
   - Check Facebook Custom Audience

### Automated Process

1. **Setup Auto-Download** (if Retran.com supports):
   ```python
   # Add to lead_processor.py
   def download_retran_data():
       # Implement Retran.com API download
       pass
   ```

2. **Schedule Processing**:
   - Cron job runs daily
   - Processes new leads
   - Syncs to all platforms

## 🎯 Marketing Campaign Setup

### Mailchimp Email Sequence

1. **Create Automation**:
   - Mailchimp → Automations → Create
   - Trigger: Tag added "foreclosure-lead"

2. **Email Sequence**:
   ```
   Day 0: "Stop Your Foreclosure Today" (Immediate)
   Day 2: "You Still Have Options" (Follow-up)
   Day 5: "Time is Running Out" (Urgency)
   Day 7: "Last Chance to Save Your Home" (Final)
   ```

3. **Email Templates**:
   - Subject: "Stop Foreclosure in 7 Days - {First Name}"
   - CTA: "Call (555) STOP-NOW Now"
   - Personalization: Use merge fields

### Twilio SMS Campaign

**Sample Messages**:
```
Day 0: "URGENT: Stop foreclosure now! We can close in 7 days. Call (555) STOP-NOW"
Day 3: "Don't lose your home! Get cash offer today. Call (555) STOP-NOW"
Day 7: "Final notice: Foreclosure can still be stopped. Call now (555) STOP-NOW"
```

### Google Ads Campaign

1. **Campaign Type**: Search
2. **Keywords**:
   - "stop foreclosure"
   - "avoid foreclosure"
   - "sell house fast foreclosure"
   - "foreclosure help"

3. **Ad Copy**:
   ```
   Stop Foreclosure in 7 Days
   Get Cash for Your Home - No Fees
   Licensed Real Estate Professionals
   Call (555) STOP-NOW Now
   ```

4. **Custom Audience**: Use uploaded Retran leads for Similar Audiences

### Facebook Ads Campaign

1. **Campaign Objective**: Lead Generation
2. **Audience**:
   - Custom Audience: Uploaded Retran leads
   - Lookalike Audience: 1% similar to custom audience
   - Interest Targeting: Homeownership, Real Estate

3. **Ad Creative**:
   - Image: Happy family, house
   - Headline: "Stop Foreclosure Fast"
   - Text: "Facing foreclosure? Get cash for your home in 7 days."
   - CTA: "Learn More"

## 🔒 Security & Compliance

### Data Protection

1. **Environment Variables**: Never commit API keys to Git
2. **Data Encryption**: Hash emails/phones for platform sync
3. **Data Retention**: Implement data purging policies

### Legal Compliance

1. **CAN-SPAM**: Include unsubscribe in all emails
2. **TCPA**: Get consent for SMS marketing
3. **GDPR**: Handle data deletion requests
4. **State Laws**: Check foreclosure rescue laws by state

### Privacy Policy

Include privacy policy on website covering:
- Data collection practices
- Third-party integrations
- Cookie usage
- Contact information

## 🚨 Troubleshooting

### Common Issues

1. **GitHub Pages Not Loading**:
   - Check repository is public
   - Verify Pages settings
   - Allow up to 10 minutes for deployment

2. **Contact Form Not Working**:
   - Check Google Apps Script deployment
   - Verify Web App permissions
   - Test with browser console open

3. **Python Script Errors**:
   - Check API key validity
   - Verify CSV column names match
   - Check internet connection

4. **API Rate Limits**:
   - Hunter.io: 25 requests/month (free)
   - Apollo.io: 60 requests/month (free)
   - Add delays between requests

### Monitoring & Alerts

1. **Setup Notifications**:
   ```python
   # Add to lead_processor.py
   def send_alert(message):
       # Send email/SMS alert for errors
       pass
   ```

2. **Track Success Metrics**:
   - Leads processed daily
   - Email enrichment rate
   - Platform sync success rate

## 📈 Performance Optimization

### Website Speed

1. **Optimize Images**: Compress images to <100KB
2. **CDN**: Use GitHub Pages CDN
3. **Minify CSS/JS**: Use build tools for production

### Lead Processing

1. **Batch Processing**: Process leads in batches
2. **Parallel API Calls**: Use async/await for enrichment
3. **Caching**: Cache enriched data to avoid re-processing

### Conversion Optimization

1. **A/B Testing**: Test different headlines and CTAs
2. **Mobile Optimization**: Ensure mobile-first design
3. **Page Speed**: Target <3 second load times

## 📞 Support

For technical support:
- Email: tech@stopforeclosurefast.com
- Phone: (555) STOP-NOW
- Documentation: [GitHub Wiki](https://github.com/yourusername/stop-foreclosure-fast/wiki)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
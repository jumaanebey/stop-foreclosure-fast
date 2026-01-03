# 🚀 Google AI Workflows - Complete Deployment Guide

## Quick Start (30 minutes)

### Prerequisites
- Google Cloud Account with billing enabled
- Node.js 18+ installed
- Domain verified in Google Search Console (for email)

---

## Step 1: Initial Setup (5 minutes)

```bash
# Clone and setup
cd google-ai-setup
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Required Environment Variables
```env
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./foreclosure-ai-key.json
GOOGLE_PROJECT_ID=foreclosure-ai-assistant

# Gemini API
VERTEX_AI_LOCATION=us-central1

# Email
EMAIL_USER=help@myforeclosuresolution.com
EMAIL_APP_PASSWORD=your-app-password

# Twilio (SMS)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE=+1949xxxxxxx

# Slack (Alerts)
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx

# Google Sheets
SHEET_ID=1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU
```

---

## Step 2: Deploy Cloud Functions (10 minutes)

### Deploy All Functions
```bash
npm run deploy:all
```

### Or Deploy Individually
```bash
# Lead Qualification Bot
npm run deploy:lead-bot

# Document Processor
npm run deploy:doc-processor

# Email Automation
npm run deploy:email

# Voice Assistant Webhook
npm run deploy:dialogflow
```

### Verify Deployment
```bash
gcloud functions list
```

You should see:
- ✅ qualifyForeclosureLead
- ✅ processForeclosureDocument
- ✅ processForeclosureEmail
- ✅ dialogflowWebhook

---

## Step 3: Configure Dialogflow (10 minutes)

### Import Configuration
```bash
# Install Dialogflow CLI
npm install -g @google-cloud/dialogflow-cx-cli

# Create agent
cxcli agent create --project foreclosure-ai-assistant \
  --location us-central1 \
  --display-name "Foreclosure Help Assistant"

# Import configuration
cxcli restore --agent-name "Foreclosure Help Assistant" \
  --input-file ./dialogflow-config.yaml
```

### Connect Phone Number
1. Go to [Dialogflow Console](https://dialogflow.cloud.google.com/cx)
2. Select your agent
3. Go to Integrations → Telephony
4. Add phone number: +1-949-565-5285

---

## Step 4: Website Integration (5 minutes)

### Add to Your Website

```html
<!-- Add to index.html -->
<script src="https://apis.google.com/js/api.js"></script>
<script>
// Lead Qualification
async function qualifyLead(formData) {
    const response = await fetch('https://us-central1-foreclosure-ai-assistant.cloudfunctions.net/qualifyForeclosureLead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    });
    return response.json();
}

// Document Upload
async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('document', file);
    formData.append('documentType', 'notice_of_default');

    const response = await fetch('https://us-central1-foreclosure-ai-assistant.cloudfunctions.net/processForeclosureDocument', {
        method: 'POST',
        body: formData
    });
    return response.json();
}
</script>
```

---

## Step 5: Test Everything

### Test Lead Qualification
```bash
curl -X POST https://us-central1-foreclosure-ai-assistant.cloudfunctions.net/qualifyForeclosureLead \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "foreclosureStage": "notice_of_default",
    "timelineUrgency": "7 days",
    "monthsBehind": 3
  }'
```

### Test Voice Assistant
```bash
# Call your Dialogflow phone number
# Say: "I need urgent help with foreclosure"
```

---

## 📊 Monitoring & Analytics

### View Logs
```bash
gcloud functions logs read qualifyForeclosureLead --limit 50
```

### Set Up Monitoring Dashboard
1. Go to [Cloud Console](https://console.cloud.google.com)
2. Navigate to Monitoring → Dashboards
3. Create dashboard with:
   - Function invocations
   - Error rate
   - Latency (p50, p95, p99)
   - Cost tracking

### Set Budget Alerts
```bash
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="AI Workflows Budget" \
  --budget-amount=200USD \
  --threshold-rule=percent=50,color=YELLOW \
  --threshold-rule=percent=90,color=RED
```

---

## 🔒 Security Checklist

- [ ] API keys stored in Secret Manager
- [ ] Cloud Functions use least privilege IAM
- [ ] HTTPS only endpoints
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] PII data encrypted at rest
- [ ] Audit logging enabled

---

## 💰 Cost Optimization

### Estimated Monthly Costs
| Service | Usage | Cost |
|---------|-------|------|
| Gemini API | 1000 requests/day | $50 |
| Cloud Functions | 50K invocations | $10 |
| Dialogflow | 500 voice minutes | $25 |
| Document AI | 500 documents | $25 |
| **Total** | | **~$110/month** |

### Cost Saving Tips
1. Use Cloud Scheduler for batch processing
2. Enable function concurrency
3. Set max instances to prevent runaway costs
4. Use Firestore for caching Gemini responses

---

## 🚨 Troubleshooting

### Common Issues

**Function timeout errors**
```bash
gcloud functions deploy FUNCTION_NAME --timeout=540s
```

**Gemini API rate limits**
```javascript
// Add exponential backoff
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 2 ** i * 1000));
    }
  }
}
```

**Dialogflow not responding**
- Check webhook URL in Dialogflow console
- Verify Cloud Function is deployed
- Check logs: `gcloud functions logs read dialogflowWebhook`

---

## 📈 Next Steps

1. **A/B Testing**: Test different Gemini prompts for better conversion
2. **Multi-language**: Add Spanish language support
3. **Advanced Analytics**: Connect to BigQuery for ML insights
4. **Mobile App**: Build React Native app with same APIs
5. **WhatsApp Bot**: Add WhatsApp Business API integration

---

## 🆘 Support

- **Documentation**: [Google Cloud AI Docs](https://cloud.google.com/vertex-ai/docs)
- **Community**: [Google Cloud Community](https://cloud.google.com/community)
- **Issues**: Create issue in GitHub repo
- **Email**: help@myforeclosuresolution.com

---

**Remember**: Test in staging before production! 🚀
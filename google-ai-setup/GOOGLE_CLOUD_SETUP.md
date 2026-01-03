# Google Cloud AI Setup for Foreclosure Solution

## Quick Start Guide

### Step 1: Google Cloud Project Setup

```bash
# Install Google Cloud CLI
brew install google-cloud-sdk  # Mac
# Or download from: https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init
gcloud auth login

# Create new project
gcloud projects create foreclosure-ai-assistant --name="Foreclosure AI Assistant"
gcloud config set project foreclosure-ai-assistant

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudscheduler.googleapis.com \
  dialogflow.googleapis.com \
  documentai.googleapis.com \
  sheets.googleapis.com \
  gmail.googleapis.com
```

### Step 2: Set up Service Account

```bash
# Create service account
gcloud iam service-accounts create foreclosure-ai \
  --display-name="Foreclosure AI Service Account"

# Download credentials
gcloud iam service-accounts keys create \
  ~/foreclosure-ai-key.json \
  --iam-account=foreclosure-ai@foreclosure-ai-assistant.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/foreclosure-ai-key.json
```

### Step 3: Enable Vertex AI & Gemini

```bash
# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Set default region
gcloud config set ai_platform/region us-central1
```

## Pricing Estimates

### Monthly Costs (Estimated)
- **Gemini API**: ~$50-100 (1000 requests/day)
- **Cloud Functions**: ~$10-20
- **Dialogflow**: ~$20-40 (voice minutes)
- **Document AI**: ~$30-50 (1000 documents)
- **Total**: ~$110-210/month

### Free Tier Includes
- 2 million Cloud Function invocations/month
- $300 credit for new accounts
- 500 API calls/month to Gemini

## Security Best Practices

1. **Never commit credentials to Git**
   ```bash
   echo "*.json" >> .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use Secret Manager for production**
   ```bash
   gcloud secrets create api-keys --data-file=.env
   ```

3. **Set up budget alerts**
   ```bash
   gcloud billing budgets create \
     --billing-account=YOUR_BILLING_ID \
     --display-name="Foreclosure AI Budget" \
     --budget-amount=200 \
     --threshold-rule=percent=80
   ```

## Next Steps

1. ✅ Complete Google Cloud setup
2. → Build Lead Qualification Bot
3. → Implement Document Processing
4. → Create Email Automation
5. → Set up Voice Assistant
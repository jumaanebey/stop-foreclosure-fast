#!/bin/bash

# Google Cloud Run Deployment Script for Foreclosure AI
# Run this script to deploy your Python AI to Google Cloud Run (FREE)

echo "🚀 Deploying Foreclosure AI to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Installing..."
    echo "Please visit: https://cloud.google.com/sdk/docs/install"
    echo "Or run: curl https://sdk.cloud.google.com | bash"
    exit 1
fi

# Set project variables
PROJECT_ID="foreclosure-ai-$(date +%s)"
SERVICE_NAME="foreclosure-ai-api"
REGION="us-central1"

echo "📋 Project ID: $PROJECT_ID"
echo "🌐 Service: $SERVICE_NAME"
echo "📍 Region: $REGION"

# Authenticate with Google Cloud (if needed)
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Create new project (or use existing)
echo "🆕 Setting up Google Cloud project..."
gcloud projects create $PROJECT_ID --name="Foreclosure AI" 2>/dev/null || true
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Build and deploy to Cloud Run
echo "🏗️ Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production,PORT=8080" \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "📍 Your AI API is live at: $SERVICE_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Set environment variables in Google Cloud Console:"
echo "   - EMAIL_USER=help@myforeclosuresolution.com"
echo "   - EMAIL_PASSWORD=your-gmail-app-password"
echo "   - ALLOWED_ORIGINS=https://myforeclosuresolution.com"
echo ""
echo "2. Test your API:"
echo "   curl $SERVICE_URL/api/ai/health"
echo ""
echo "3. Update your website to use: $SERVICE_URL"
echo ""
echo "💰 Cost: FREE (2M requests/month included)"
echo "📊 Monitor usage: https://console.cloud.google.com/run"

# Save deployment info
cat > deployment-info.txt << EOF
Deployment Information:
======================
Project ID: $PROJECT_ID
Service Name: $SERVICE_NAME
Region: $REGION
API URL: $SERVICE_URL
Deployed: $(date)

Environment Variables to Set:
============================
EMAIL_USER=help@myforeclosuresolution.com
EMAIL_PASSWORD=your-gmail-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ALLOWED_ORIGINS=https://myforeclosuresolution.com,https://www.myforeclosuresolution.com

Test Commands:
==============
Health Check: curl $SERVICE_URL/api/ai/health
Dashboard: $SERVICE_URL/dashboard.html
EOF

echo "📄 Deployment info saved to: deployment-info.txt"
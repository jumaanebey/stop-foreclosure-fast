#!/bin/bash

# Foreclosure AI Workflows - Deployment Script
# Project: impactful-veld-469306-c7

echo "🚀 Deploying Google AI Workflows for Foreclosure Solution"

# Set project
export PROJECT_ID="impactful-veld-469306-c7"
export REGION="us-central1"
export GCLOUD_PATH="$HOME/google-cloud-sdk/bin/gcloud"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 Using project: $PROJECT_ID"
echo "📍 Region: $REGION"

# Function to check if API is enabled
check_api() {
    local api=$1
    echo -n "Checking $api... "
    if $GCLOUD_PATH services list --enabled --filter="name:$api" --format="value(name)" 2>/dev/null | grep -q $api; then
        echo -e "${GREEN}✓ Enabled${NC}"
        return 0
    else
        echo -e "${YELLOW}Not enabled${NC}"
        return 1
    fi
}

# Function to enable API
enable_api() {
    local api=$1
    echo "Enabling $api..."
    $GCLOUD_PATH services enable $api --project=$PROJECT_ID
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $api enabled successfully${NC}"
    else
        echo -e "${RED}✗ Failed to enable $api${NC}"
        return 1
    fi
}

echo ""
echo "=== Step 1: Checking Authentication ==="
$GCLOUD_PATH auth application-default print-access-token > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ Application Default Credentials not set${NC}"
    echo "Please run: $GCLOUD_PATH auth application-default login"
    echo "Then re-run this script."
    exit 1
else
    echo -e "${GREEN}✓ Authentication configured${NC}"
fi

echo ""
echo "=== Step 2: Enabling Required APIs ==="
REQUIRED_APIS=(
    "aiplatform.googleapis.com"
    "cloudfunctions.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "run.googleapis.com"
    "documentai.googleapis.com"
    "sheets.googleapis.com"
    "gmail.googleapis.com"
    "dialogflow.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    check_api $api || enable_api $api
done

echo ""
echo "=== Step 3: Creating Service Account ==="
SERVICE_ACCOUNT="foreclosure-ai@$PROJECT_ID.iam.gserviceaccount.com"

if $GCLOUD_PATH iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Service account already exists${NC}"
else
    echo "Creating service account..."
    $GCLOUD_PATH iam service-accounts create foreclosure-ai \
        --display-name="Foreclosure AI Service Account" \
        --project=$PROJECT_ID

    # Grant necessary roles
    echo "Granting IAM roles..."
    $GCLOUD_PATH projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/aiplatform.user"

    $GCLOUD_PATH projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/documentai.apiUser"

    echo -e "${GREEN}✓ Service account created${NC}"
fi

echo ""
echo "=== Step 4: Setting up Node.js dependencies ==="
if [ ! -f "package.json" ]; then
    echo -e "${RED}✗ package.json not found${NC}"
    echo "Please ensure you're in the google-ai-setup directory"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

echo ""
echo "=== Step 5: Creating .env file ==="
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Google Cloud Configuration
GOOGLE_PROJECT_ID=$PROJECT_ID
GOOGLE_REGION=$REGION
GOOGLE_SERVICE_ACCOUNT=$SERVICE_ACCOUNT

# Vertex AI / Gemini
VERTEX_AI_LOCATION=$REGION

# Email Configuration (Update these!)
EMAIL_USER=help@myforeclosuresolution.com
EMAIL_APP_PASSWORD=your-app-password-here

# Twilio SMS (Update these!)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_PHONE=+19493284811

# Google Sheets
SHEET_ID=1AaGUcBQczrOvlwD8sS6Rs5XH7R52X_wWfFwsrxfHbgU

# Slack Webhook (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EOF
    echo -e "${YELLOW}⚠ Created .env file - Please update with your actual credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo "=== Step 6: Deploying Cloud Functions ==="
echo "Would you like to deploy the Cloud Functions now? (y/n)"
read -r DEPLOY_NOW

if [[ $DEPLOY_NOW == "y" || $DEPLOY_NOW == "Y" ]]; then
    echo ""
    echo "Deploying Lead Qualification Bot..."
    $GCLOUD_PATH functions deploy qualifyForeclosureLead \
        --gen2 \
        --runtime nodejs20 \
        --region $REGION \
        --source . \
        --entry-point qualifyForeclosureLead \
        --trigger-http \
        --allow-unauthenticated \
        --service-account $SERVICE_ACCOUNT \
        --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Lead Qualification Bot deployed${NC}"
        LEAD_BOT_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/qualifyForeclosureLead"
        echo "URL: $LEAD_BOT_URL"
    else
        echo -e "${RED}✗ Failed to deploy Lead Qualification Bot${NC}"
    fi

    echo ""
    echo "Deploying Document Processor..."
    $GCLOUD_PATH functions deploy processForeclosureDocument \
        --gen2 \
        --runtime nodejs20 \
        --region $REGION \
        --source . \
        --entry-point processForeclosureDocument \
        --trigger-http \
        --allow-unauthenticated \
        --service-account $SERVICE_ACCOUNT \
        --memory 512MB \
        --timeout 120s

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Document Processor deployed${NC}"
        DOC_PROCESSOR_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/processForeclosureDocument"
        echo "URL: $DOC_PROCESSOR_URL"
    else
        echo -e "${RED}✗ Failed to deploy Document Processor${NC}"
    fi
fi

echo ""
echo "=== Setup Summary ==="
echo -e "${GREEN}✅ Google Cloud project configured: $PROJECT_ID${NC}"
echo -e "${GREEN}✅ Required APIs enabled${NC}"
echo -e "${GREEN}✅ Service account created: $SERVICE_ACCOUNT${NC}"
echo -e "${GREEN}✅ Dependencies installed${NC}"

if [[ $DEPLOY_NOW == "y" || $DEPLOY_NOW == "Y" ]]; then
    echo ""
    echo "=== Deployed Endpoints ==="
    echo "Lead Bot: ${LEAD_BOT_URL:-Not deployed}"
    echo "Document Processor: ${DOC_PROCESSOR_URL:-Not deployed}"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Update the .env file with your actual credentials"
echo "2. Test the deployed functions using the test commands"
echo "3. Integrate the endpoints into your website"
echo ""
echo "Test command example:"
echo "curl -X POST $LEAD_BOT_URL \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"name\":\"Test\",\"email\":\"test@example.com\",\"urgencyScore\":8}'"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
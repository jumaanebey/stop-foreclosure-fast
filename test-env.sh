#!/bin/bash
# Quick test to verify your .env is working

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Test if keys are loaded
if [ -z "$CONVERTKIT_API_KEY" ]; then
    echo "❌ CONVERTKIT_API_KEY not found in .env"
else
    echo "✅ ConvertKit API Key loaded: ${CONVERTKIT_API_KEY:0:8}..."
fi

if [ -z "$CONVERTKIT_API_SECRET" ]; then
    echo "❌ CONVERTKIT_API_SECRET not found in .env"
else
    echo "✅ ConvertKit API Secret loaded: ${CONVERTKIT_API_SECRET:0:8}..."
fi

if [ -z "$NOTIFICATION_EMAIL" ]; then
    echo "❌ NOTIFICATION_EMAIL not found in .env"
else
    echo "✅ Notification Email: $NOTIFICATION_EMAIL"
fi

echo ""
echo "🔍 Security Check:"
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ WARNING: .env is tracked by Git! Run: git rm --cached .env"
else
    echo "✅ .env is properly ignored by Git"
fi

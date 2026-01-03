#!/bin/bash

# Secure Environment Setup Script for New Developers
# This helps you set up API keys safely without exposing them

set -e  # Exit on any error

echo "🔒 Setting up secure environment for MyForeclosureSolutions.com"
echo "============================================================"

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Existing .env file preserved."
        exit 0
    fi
fi

# Create .env from template
if [ -f ".env.template" ]; then
    echo "📋 Creating .env from template..."
    cp .env.template .env
    chmod 600 .env  # Secure permissions
    echo "✅ .env file created with secure permissions (only you can read it)"
else
    echo "❌ .env.template not found! Please run this from the project root directory."
    exit 1
fi

# Ensure .gitignore includes .env
echo "🔒 Securing .env from Git..."
if ! grep -q "^.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
else
    echo "✅ .env already in .gitignore"
fi

if ! grep -q "^\*.env$" .gitignore 2>/dev/null; then
    echo "*.env" >> .gitignore
    echo "✅ Added *.env pattern to .gitignore"
fi

# Check Git status
echo ""
echo "🔍 Checking Git status..."
if git status --porcelain | grep -q ".env"; then
    echo "⚠️  WARNING: .env file is being tracked by Git!"
    echo "   Run: git rm --cached .env"
    echo "   Then: git commit -m 'Remove .env from tracking'"
else
    echo "✅ .env file is properly ignored by Git"
fi

echo ""
echo "📝 NEXT STEPS:"
echo "=============="
echo "1. Get your NEW ConvertKit API keys:"
echo "   → Go to: https://app.convertkit.com/account_settings/advanced_settings"
echo "   → Click 'Regenerate API Key' (to invalidate the old exposed ones)"
echo "   → Copy your NEW API Key and Secret"
echo ""
echo "2. Edit the .env file:"
echo "   → Open: .env"
echo "   → Replace 'your-new-convertkit-api-key-here' with your actual key"
echo "   → Replace 'your-new-convertkit-api-secret-here' with your actual secret"
echo "   → Update other values as needed"
echo ""
echo "3. Test your setup:"
echo "   → Run: source .env && echo \"API Key loaded: \${CONVERTKIT_API_KEY:0:8}...\""
echo "   → You should see the first 8 characters of your key"
echo ""
echo "4. NEVER commit .env to Git!"
echo "   → Always check 'git status' before committing"
echo "   → The .env file should NOT appear in the list"
echo ""
echo "🎉 Setup complete! Your API keys will now be secure."
echo ""
echo "💡 Pro Tip: Create different .env files for development and production:"
echo "   → .env.development (for testing)"
echo "   → .env.production (for live site)"
echo "   → Keep them separate and secure!"

# Create a quick test script
cat > test-env.sh << 'EOF'
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
EOF

chmod +x test-env.sh
echo ""
echo "🧪 Created test-env.sh - run it to verify your setup!"
echo "   → ./test-env.sh"
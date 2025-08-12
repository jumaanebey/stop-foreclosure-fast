# GitHub Repository Setup Instructions

## 1. Create GitHub Repository

### Option A: Via GitHub Website
1. Go to [GitHub.com](https://github.com)
2. Click the "+" icon → "New repository"
3. Repository name: `stop-foreclosure-fast`
4. Description: `Complete pre-foreclosure marketing system with sales funnel website and lead processing automation`
5. Make it **Public** (required for GitHub Pages)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### Option B: Via GitHub CLI (if you have gh installed)
```bash
gh repo create stop-foreclosure-fast --public --description "Complete pre-foreclosure marketing system with sales funnel website and lead processing automation"
```

## 2. Connect Local Repository to GitHub

After creating the repository, copy the repository URL and run:

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/stop-foreclosure-fast.git

# Push to GitHub
git push -u origin main
```

## 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click the "Settings" tab
3. Scroll down to "Pages" section in the left sidebar
4. Under "Source", select "Deploy from a branch"
5. Branch: "main"
6. Folder: "/ (root)"
7. Click "Save"

## 4. Your Website Will Be Live At:
```
https://YOUR_USERNAME.github.io/stop-foreclosure-fast/
```

**Note**: It may take up to 10 minutes for the site to become available after enabling Pages.

## 5. Configure the Website

After deployment, update these placeholders:

### Analytics IDs (in index.html and thank-you.html):
- Replace `GA_MEASUREMENT_ID` with your Google Analytics 4 ID
- Replace `YOUR_PIXEL_ID` with your Facebook Pixel ID

### Contact Information:
- Replace `(555) STOP-NOW` with your actual phone number
- Replace `help@stopforeclosurefast.com` with your actual email

### Google Sheets Integration (in js/script.js):
- Replace `YOUR_SCRIPT_ID` with your Google Apps Script Web App URL

## 6. Test Your Website

1. Visit your GitHub Pages URL
2. Test the contact form
3. Verify phone number links work
4. Check that all pages load correctly

## 7. Next Steps

1. Set up your API keys for the Python lead processor
2. Configure your marketing automation platforms
3. Start driving traffic to your website!

## Troubleshooting

### GitHub Pages Not Working?
- Ensure repository is public
- Check that Pages is enabled in Settings
- Wait up to 10 minutes for initial deployment
- Check for any build errors in Settings → Pages

### Contact Form Issues?
- Set up Google Apps Script Web App
- Update the script URL in js/script.js
- Test form submission with browser console open

## Repository URL Format
Your repository will be at: `https://github.com/YOUR_USERNAME/stop-foreclosure-fast`
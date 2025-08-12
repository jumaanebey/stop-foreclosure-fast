#!/bin/bash

# Quick Deployment Script for Stop Foreclosure Fast
# This script helps deploy your marketing system to GitHub

echo "🚀 Stop Foreclosure Fast - Deployment Script"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Please run this script from the project root directory."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Complete pre-foreclosure marketing system"
    git branch -M main
fi

# Get GitHub username
echo ""
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

# Repository name
repo_name="stop-foreclosure-fast"

echo ""
echo "📋 Next steps:"
echo "1. Create a GitHub repository manually:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $repo_name"
echo "   - Make it PUBLIC (required for GitHub Pages)"
echo "   - Don't initialize with README, .gitignore, or license"
echo ""
echo "2. After creating the repository, run these commands:"
echo ""
echo "   git remote add origin https://github.com/$github_username/$repo_name.git"
echo "   git push -u origin main"
echo ""
echo "3. Enable GitHub Pages:"
echo "   - Go to Settings → Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main / (root)"
echo ""
echo "4. Your website will be live at:"
echo "   https://$github_username.github.io/$repo_name/"
echo ""

# Option to automatically set up remote if user confirms
echo ""
read -p "Have you created the GitHub repository? (y/n): " created_repo

if [ "$created_repo" = "y" ] || [ "$created_repo" = "Y" ]; then
    echo ""
    echo "🔗 Adding GitHub remote..."
    git remote add origin "https://github.com/$github_username/$repo_name.git" 2>/dev/null || echo "Remote already exists"
    
    echo "📤 Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully deployed to GitHub!"
        echo ""
        echo "🌐 Repository: https://github.com/$github_username/$repo_name"
        echo "🌐 Website: https://$github_username.github.io/$repo_name/"
        echo ""
        echo "📝 Don't forget to:"
        echo "   1. Enable GitHub Pages in repository Settings"
        echo "   2. Replace placeholder analytics IDs"
        echo "   3. Update contact information"
        echo "   4. Set up your API keys for lead processing"
    else
        echo "❌ Failed to push to GitHub. Please check your repository settings."
    fi
else
    echo ""
    echo "📝 Manual setup required:"
    echo "   1. Create repository at: https://github.com/new"
    echo "   2. Run: git remote add origin https://github.com/$github_username/$repo_name.git"
    echo "   3. Run: git push -u origin main"
fi

echo ""
echo "📖 See setup-github.md for detailed instructions"
echo "🎯 Ready to start capturing foreclosure leads!"
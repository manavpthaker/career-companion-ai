#!/bin/bash

echo "🚀 Push CareerCompanion AI to GitHub"
echo "===================================="
echo ""
echo "Step 1: Create repository on GitHub.com"
echo "----------------------------------------"
echo "Go to: https://github.com/new"
echo ""
echo "Use these settings:"
echo "  Name: career-companion-ai"
echo "  Description: AI-powered platform giving job seekers an entire career support team."
echo "  Visibility: Public"
echo "  DON'T initialize with README/gitignore/license"
echo ""
echo "Press Enter after creating the repository on GitHub..."
read

echo ""
echo "Step 2: Adding remote and pushing"
echo "----------------------------------------"

# Add the remote
git remote add origin https://github.com/manavthaker/career-companion-ai.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your repository should now be live at:"
echo "https://github.com/manavthaker/career-companion-ai"
echo ""
echo "Next steps:"
echo "1. Add topics: job-search, ai, career, automation, ethics"
echo "2. Pin the repository on your profile"
echo "3. Share with the community!"
echo "4. Set up GitHub Pages if you want a website"
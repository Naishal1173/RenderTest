@echo off
echo 🚀 PDF Document Chatbot - GitHub Deployment Script
echo ================================================

echo.
echo 📋 Step 1: Initializing Git repository...
git init

echo.
echo 📁 Step 2: Adding all files...
git add .

echo.
echo 💾 Step 3: Creating initial commit...
git commit -m "Enhanced PDF Document Chatbot - Ready for Render deployment"

echo.
echo 🌐 Step 4: Setting up GitHub remote...
echo Please enter your GitHub username:
set /p username="GitHub Username: "

git remote add origin https://github.com/%username%/pdf-document-chatbot.git
git branch -M main

echo.
echo 📤 Step 5: Pushing to GitHub...
echo Note: You may need to enter your GitHub credentials
git push -u origin main

echo.
echo ✅ SUCCESS! Your code is now on GitHub
echo.
echo 🎯 Next Steps:
echo 1. Go to render.com and create a free account
echo 2. Click "New +" → "Web Service"
echo 3. Connect your GitHub repository: pdf-document-chatbot
echo 4. Render will auto-detect the configuration
echo 5. Click "Create Web Service"
echo 6. Wait 2-3 minutes for deployment
echo 7. Get your live URL!
echo.
echo 📖 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md
echo.
pause
# 🚀 Quick Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### 1. Go to Streamlit Cloud
Visit: **https://share.streamlit.io/**

### 2. Sign In
Click "Sign in" and authorize with your GitHub account

### 3. Deploy New App
Click the **"New app"** button

### 4. Configure App Settings

Fill in the form:
- **Repository**: `Mohit4Maq/news-checker` (or your fork)
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL** (optional): Choose something like `news-checker` or `indian-news-analyzer`

### 5. Add Your OpenAI API Key (IMPORTANT!)

1. Click **"Advanced settings"** at the bottom
2. Click on **"Secrets"** tab
3. Add this in the secrets editor:

```toml
OPEN_AI_API = "sk-your-actual-openai-api-key-here"
```

**Important**: Replace `sk-your-actual-openai-api-key-here` with your real OpenAI API key!

4. Click **"Save"**

### 6. Deploy!

Click the **"Deploy"** button and wait 1-2 minutes.

### 7. Your App is Live! 🎉

Your app will be available at:
**`https://your-app-name.streamlit.app`**

You can share this URL with anyone!

## 🔄 Updating Your App

Any time you push changes to GitHub:
```bash
git push origin main
```

Streamlit Cloud will automatically redeploy your app!

## ⚠️ Troubleshooting

### App won't start?
- Check that `OPEN_AI_API` is set in Secrets
- Verify your API key is valid
- Check the logs in Streamlit Cloud dashboard

### API errors?
- Verify your OpenAI API key has credits
- Check API key is correctly set in Secrets (no extra quotes/spaces)

### Need help?
- Check Streamlit Cloud logs: Click on your app → "Manage app" → "Logs"
- Review error messages in the app itself

## 💡 Tips

- Your app URL is shareable - anyone can use it!
- Monitor your OpenAI API usage to control costs
- The app automatically redeploys on every push to main branch


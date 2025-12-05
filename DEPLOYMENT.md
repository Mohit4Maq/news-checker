# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### Step 1: Prepare Repository
✅ Repository is already public: https://github.com/Mohit4Maq/news-checker
✅ All files are committed and pushed

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure your app**:
   - **Repository**: `Mohit4Maq/news-checker`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain like `news-checker` or `indian-news-checker`

5. **Add Secrets** (Environment Variables):
   - Click "Advanced settings"
   - Add secret: `OPEN_AI_API` = `your-openai-api-key-here`
   - This will be available as an environment variable

6. **Click "Deploy"**

7. **Wait for deployment** (usually 1-2 minutes)

8. **Your app will be live at**: `https://your-app-name.streamlit.app`

## Environment Variables

The app uses `OPEN_AI_API` from environment variables. In Streamlit Cloud:
- Go to your app settings
- Click "Secrets"
- Add: `OPEN_AI_API = "your-key-here"`

## Troubleshooting

### If deployment fails:
1. Check that `requirements.txt` includes all dependencies
2. Verify `app.py` is in the root directory
3. Check Streamlit Cloud logs for errors
4. Ensure API key is set in Secrets

### If app loads but API calls fail:
1. Verify `OPEN_AI_API` secret is set correctly
2. Check API key has sufficient credits
3. Review error messages in the app

## Updating the App

Simply push changes to the `main` branch and Streamlit Cloud will automatically redeploy!

```bash
git add .
git commit -m "Your changes"
git push origin main
```


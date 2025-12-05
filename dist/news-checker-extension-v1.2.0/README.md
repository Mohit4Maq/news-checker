# News Checker Chrome Extension

A Chrome extension that allows you to quickly analyze news articles with one click. Send any news article URL directly to your News Checker Streamlit app.

## Features

- 🔍 **One-Click Analysis**: Click the extension icon and analyze the current article
- 📋 **Copy URL**: Quickly copy article URL to clipboard
- ⚙️ **Configurable**: Set your Streamlit app URL
- 🚀 **Fast**: Opens Streamlit app with URL pre-filled

## Installation

### Method 1: Load Unpacked (Development)

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` folder
5. The extension icon should appear in your toolbar

### Method 2: Pack Extension (For Distribution)

1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Pack extension"
4. Select the `chrome_extension` folder
5. This creates a `.crx` file you can distribute

## Setup

1. **Install the extension** (see above)

2. **Get your Streamlit app URL**
   - Deploy your app on Streamlit Cloud
   - Copy the URL (e.g., `https://your-app.streamlit.app`)

3. **Configure the extension**
   - Click the extension icon
   - Enter your Streamlit app URL in the settings
   - Click "Save" (auto-saves)

## Usage

1. **Navigate to a news article** you want to analyze
2. **Click the extension icon** in Chrome toolbar
3. **Click "🔍 Analyze This Article"**
4. The Streamlit app opens with the article URL pre-filled
5. The app automatically starts analyzing!

## How It Works

- Extension captures the current page URL
- Opens Streamlit app with URL as query parameter: `?url=ARTICLE_URL`
- Streamlit app detects the URL parameter and auto-analyzes

## Requirements

- Chrome browser (or Chromium-based browsers)
- Streamlit app deployed and accessible
- Internet connection

## Troubleshooting

**Extension doesn't appear?**
- Make sure Developer mode is enabled
- Check for errors in `chrome://extensions/`

**URL not opening?**
- Verify your Streamlit app URL is correct
- Make sure the app is deployed and accessible
- Check browser console for errors

**Analysis doesn't start automatically?**
- Make sure the Streamlit app is updated with URL parameter support
- Check that the URL parameter is being passed correctly

## Version

- Extension: v1.0.0
- Compatible with News Checker: v1.2.0+


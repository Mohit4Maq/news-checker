# Chrome Extension Installation Guide

## Quick Install (5 minutes)

### Step 1: Download Extension Files
The extension files are in the `chrome_extension` folder.

### Step 2: Create Extension Icons (Optional but Recommended)
You can create simple icons or use emoji-based icons. For now, create placeholder icons:

**Option A: Use Online Icon Generator**
1. Go to https://www.favicon-generator.org/ or similar
2. Upload a 128x128 image with 📰 emoji or news icon
3. Download and extract icons to `chrome_extension/icons/` folder
4. Name them: `icon16.png`, `icon48.png`, `icon128.png`

**Option B: Create Simple Placeholder Icons**
Create 3 PNG files:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)  
- `icon128.png` (128x128 pixels)

You can use any image editor or online tool.

### Step 3: Load Extension in Chrome

1. **Open Chrome Extensions Page**
   - Go to: `chrome://extensions/`
   - Or: Menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle "Developer mode" switch in top-right corner

3. **Load the Extension**
   - Click "Load unpacked" button
   - Navigate to and select the `chrome_extension` folder
   - Click "Select Folder"

4. **Verify Installation**
   - Extension icon should appear in Chrome toolbar
   - You should see "News Checker - Fact-Check Extension" in extensions list

### Step 4: Configure Extension

1. **Get Your Streamlit App URL**
   - Deploy your app on Streamlit Cloud
   - Copy the URL (e.g., `https://your-app-name.streamlit.app`)

2. **Set URL in Extension**
   - Click the extension icon in toolbar
   - Enter your Streamlit app URL in the settings field
   - URL is saved automatically

### Step 5: Use the Extension

1. **Navigate to any news article**
2. **Click the extension icon**
3. **Click "🔍 Analyze This Article"**
4. Streamlit app opens and automatically analyzes the article!

## Troubleshooting

**Icons missing?**
- Create placeholder icons (see Step 2)
- Or the extension will work without icons (just shows default Chrome icon)

**Extension not loading?**
- Make sure Developer mode is enabled
- Check for errors in `chrome://extensions/` (click "Errors" button)
- Verify all files are in the `chrome_extension` folder

**URL not opening?**
- Verify Streamlit app URL is correct
- Make sure app is deployed and accessible
- Check browser console for errors

## Features

✅ One-click article analysis
✅ Copy URL to clipboard
✅ Configurable Streamlit URL
✅ Auto-opens Streamlit app with article URL
✅ Works on any news website


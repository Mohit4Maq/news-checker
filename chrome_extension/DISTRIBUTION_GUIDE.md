# Chrome Extension Distribution Guide

## 📦 What Folder to Share

**Share the entire `chrome_extension` folder** - but you can create a minimal version with only essential files.

## ✅ Essential Files (Minimum Required)

For manual installation, users need these files:

```
chrome_extension/
├── manifest.json          (REQUIRED - Extension configuration)
├── popup.html             (REQUIRED - Extension UI)
├── popup.js               (REQUIRED - Extension logic)
├── content.js             (REQUIRED - Content extraction)
└── icons/                 (REQUIRED - Extension icons)
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 📋 Optional Files (Nice to Have)

These files are helpful but not required:

```
chrome_extension/
├── README.md              (Documentation)
├── install_instructions.md (Installation guide)
└── VERSION.md             (Version info)
```

## 🚀 How to Share

### Option 1: Share Entire Folder (Easiest)
1. Zip the entire `chrome_extension` folder
2. Share the ZIP file
3. Users extract and load the folder

### Option 2: Create Minimal Package (Recommended)
1. Create a new folder: `news-checker-extension`
2. Copy only essential files:
   - `manifest.json`
   - `popup.html`
   - `popup.js`
   - `content.js`
   - `icons/` folder (all 3 PNG files)
3. Optionally add `README.md` or `install_instructions.md`
4. Zip this folder
5. Share the ZIP

## 📝 Installation Instructions for Users

Share these instructions with the folder:

### Quick Install Steps:

1. **Extract the ZIP file** to a location on your computer
   - Example: `C:\Users\YourName\Downloads\news-checker-extension\`

2. **Open Chrome Extensions Page**
   - Go to: `chrome://extensions/`
   - Or: Menu (⋮) → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

4. **Load the Extension**
   - Click "Load unpacked" button
   - Navigate to and select the extracted `chrome_extension` folder
   - Click "Select Folder"

5. **Verify Installation**
   - Extension icon should appear in Chrome toolbar
   - You should see "News Checker" in the extensions list

6. **Configure Extension**
   - Click the extension icon
   - Enter your Streamlit app URL: `https://newsfactchecker.streamlit.app`
   - URL is saved automatically

7. **Use It!**
   - Navigate to any news article
   - Click the extension icon
   - Click "🔍 Analyze This Article"

## 🔗 Sharing Methods

### Method 1: GitHub Release
1. Create a GitHub release
2. Upload the ZIP file as an asset
3. Share the release link

### Method 2: Direct Download
1. Host the ZIP on a file sharing service
2. Share the download link

### Method 3: Git Repository
1. Users can clone the repo
2. Navigate to `chrome_extension/` folder
3. Load it directly

## ⚠️ Important Notes

- **Icons are required** - If missing, Chrome will show a default icon but the extension will work
- **All 4 JavaScript/HTML files are required** - Missing any will cause errors
- **manifest.json is critical** - Without it, Chrome won't recognize it as an extension
- **Users must enable Developer Mode** - This is required for unpacked extensions

## 📦 Pre-made Distribution Package

You can create a clean distribution package using:

```bash
# From project root
cd chrome_extension
zip -r ../news-checker-extension-v1.2.0.zip \
  manifest.json \
  popup.html \
  popup.js \
  content.js \
  icons/ \
  README.md \
  install_instructions.md
```

This creates a clean ZIP with only essential files.


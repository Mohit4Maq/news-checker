# 📦 What to Share for Manual Chrome Extension Installation

## ✅ Answer: Share the `chrome_extension` Folder

**Location:** `chrome_extension/` (in the project root)

## 📋 Two Options for Sharing

### Option 1: Share the Entire Folder (Easiest)
**Share this folder:** `chrome_extension/`

**What's inside:**
- ✅ All required files (manifest.json, popup.html, popup.js, content.js)
- ✅ Icons folder
- ✅ Documentation files

**How to share:**
1. Zip the entire `chrome_extension` folder
2. Share the ZIP file
3. Users extract and load it

### Option 2: Share the Distribution Package (Recommended)
**Share this file:** `dist/news-checker-extension-v1.2.0.zip`

**What's inside:**
- ✅ Only essential files (no extra documentation)
- ✅ Clean, minimal package
- ✅ Ready to distribute

**How to create:**
```bash
./chrome_extension/create_distribution_package.sh
```

This creates: `dist/news-checker-extension-v1.2.0.zip`

## 📝 Essential Files Required

Users need these files for the extension to work:

```
chrome_extension/
├── manifest.json          ✅ REQUIRED
├── popup.html             ✅ REQUIRED
├── popup.js               ✅ REQUIRED
├── content.js             ✅ REQUIRED
└── icons/                 ✅ REQUIRED
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 🚀 Installation Instructions for Users

Share these steps with the folder/ZIP:

1. **Extract the ZIP** (if shared as ZIP)
   - Extract to any location (e.g., `Downloads/news-checker-extension/`)

2. **Open Chrome Extensions**
   - Go to: `chrome://extensions/`
   - Or: Menu (⋮) → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle "Developer mode" switch (top-right)

4. **Load Extension**
   - Click "Load unpacked"
   - Select the `chrome_extension` folder (or extracted folder)
   - Click "Select Folder"

5. **Configure**
   - Click extension icon
   - Enter Streamlit URL: `https://newsfactchecker.streamlit.app`
   - URL saves automatically

6. **Use It!**
   - Go to any news article
   - Click extension icon
   - Click "🔍 Analyze This Article"

## 📦 Quick Reference

| What to Share | Location | Size | Best For |
|--------------|----------|------|----------|
| **Entire folder** | `chrome_extension/` | ~30KB | Development, full docs |
| **Distribution ZIP** | `dist/news-checker-extension-v1.2.0.zip` | ~13KB | End users, clean package |

## ✅ Recommended Approach

**For end users:** Share `dist/news-checker-extension-v1.2.0.zip`

**For developers:** Share the entire `chrome_extension/` folder or GitHub repo

## 🔗 Sharing Methods

1. **GitHub Release** - Upload ZIP as release asset
2. **Direct Download** - Host ZIP on file sharing service
3. **Git Repository** - Users clone and use `chrome_extension/` folder directly


# How to Check if Extension is Using Streamlit URL

## Method 1: Check Extension Popup (Easiest)

1. **Click the extension icon** in Chrome toolbar
2. **Look at the "Streamlit App URL" field**
   - If it shows: `https://newsfactchecker.streamlit.app` ✅ Correct
   - If it shows: `https://your-app-name.streamlit.app` ❌ Needs update
3. **If wrong, enter the correct URL** and it will save automatically

## Method 2: Check Chrome Storage (Developer Method)

1. **Open Chrome DevTools**
   - Right-click extension icon → "Inspect popup"
   - OR: Go to `chrome://extensions/` → Find extension → Click "Inspect views: service worker" or "Inspect popup"

2. **Open Console tab**

3. **Run this command:**
   ```javascript
   chrome.storage.sync.get(['streamlitUrl'], (result) => {
       console.log('Stored Streamlit URL:', result.streamlitUrl || 'Not set (using default)');
   });
   ```

4. **Expected output:**
   - `Stored Streamlit URL: https://newsfactchecker.streamlit.app` ✅
   - `Stored Streamlit URL: Not set (using default)` (will use default from code)

## Method 3: Test the Extension

1. **Navigate to any news article** (e.g., indiatoday.in)
2. **Click extension icon**
3. **Click "🔍 Analyze This Article"**
4. **Check the URL that opens:**
   - Should be: `https://newsfactchecker.streamlit.app?url=ARTICLE_URL` ✅
   - If different: Extension is using wrong URL ❌

## Method 4: Check Extension Code (Verify Default)

1. **Open extension folder:** `chrome_extension/popup.js`
2. **Look for line 2:**
   ```javascript
   const DEFAULT_STREAMLIT_URL = 'https://newsfactchecker.streamlit.app';
   ```
3. **If correct:** Extension will use this if no custom URL is set ✅

## Quick Test Script

Open Chrome DevTools Console (F12) and run:

```javascript
// Check stored URL
chrome.storage.sync.get(['streamlitUrl'], (result) => {
    const stored = result.streamlitUrl;
    const defaultUrl = 'https://newsfactchecker.streamlit.app';
    
    console.log('=== Extension URL Check ===');
    console.log('Stored URL:', stored || 'Not set');
    console.log('Default URL:', defaultUrl);
    console.log('Will use:', stored || defaultUrl);
    console.log('Status:', (stored || defaultUrl) === 'https://newsfactchecker.streamlit.app' ? '✅ Correct' : '❌ Wrong');
});
```

## Troubleshooting

**If URL is wrong:**
1. Open extension popup
2. Clear the URL field
3. Enter: `https://newsfactchecker.streamlit.app`
4. Click outside the field (auto-saves)
5. Test again

**If extension doesn't save URL:**
- Check Chrome storage permissions in manifest.json
- Should have: `"storage"` in permissions array

**If URL opens but wrong:**
- Check the URL in the popup input field
- Make sure it's saved (click outside field)
- Reload extension if needed


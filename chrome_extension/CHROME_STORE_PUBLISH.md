# Publishing News Checker Extension to Chrome Web Store

This guide will walk you through publishing the News Checker extension to the Chrome Web Store so others can easily install and use it.

## Prerequisites

1. **Google Developer Account**
   - One-time payment of $5 USD (lifetime)
   - Visit: https://chrome.google.com/webstore/devconsole
   - Sign in with your Google account
   - Pay the registration fee

2. **Extension Files Ready**
   - All files in `chrome_extension/` folder
   - Icons (16x16, 48x48, 128x128) ✅ Already have
   - Manifest.json ✅ Already have

## Step 1: Prepare Extension Package

### 1.1 Create ZIP File

**On Mac/Linux:**
```bash
cd chrome_extension
zip -r ../news-checker-extension.zip . -x "*.md" -x "*.sh" -x "test_*" -x "*.html"
cd ..
```

**On Windows:**
1. Navigate to `chrome_extension` folder
2. Select all files EXCEPT:
   - `*.md` files (documentation)
   - `*.sh` files (scripts)
   - `test_*` files
   - `QUICK_TEST.md`, `README.md`, `VERSION.md`, etc.
3. Right-click → Send to → Compressed (zipped) folder
4. Name it `news-checker-extension.zip`

**Files to INCLUDE in ZIP:**
- ✅ `manifest.json`
- ✅ `popup.html`
- ✅ `popup.js`
- ✅ `content.js`
- ✅ `icons/` folder (all icon files)

**Files to EXCLUDE from ZIP:**
- ❌ `*.md` files (README, VERSION, etc.)
- ❌ `*.sh` files (scripts)
- ❌ `test_*.html` files
- ❌ `check_url.md`, `ICON_INSTRUCTIONS.md`, etc.

### 1.2 Verify ZIP Contents

The ZIP should contain:
```
news-checker-extension.zip
├── manifest.json
├── popup.html
├── popup.js
├── content.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Step 2: Create Chrome Web Store Developer Account

1. Go to: https://chrome.google.com/webstore/devconsole
2. Sign in with your Google account
3. Click "Pay Registration Fee" ($5 USD, one-time)
4. Complete payment
5. Accept Developer Agreement

## Step 3: Upload Extension

1. Go to: https://chrome.google.com/webstore/devconsole
2. Click **"+ New Item"** button
3. Click **"Upload"** and select your `news-checker-extension.zip` file
4. Wait for upload to complete

## Step 4: Fill Store Listing

### 4.1 Basic Information

**Name:**
```
News Checker - Fact-Check Extension
```

**Summary (132 characters max):**
```
AI-powered fact-checking for Indian news. Analyze articles for propaganda, bias, and accuracy with one click.
```

**Description (Full):**
```
News Checker is a powerful Chrome extension that helps you fact-check and analyze news articles, especially Indian news, with AI-powered analysis.

🔍 KEY FEATURES:
• One-click article analysis - Extract content directly from any news website
• AI-powered fact-checking - Detects propaganda, bias, misinformation
• India-specific analysis - Understands relevance to Indian citizens
• Comprehensive scoring - Factual accuracy, source credibility, bias detection
• Citizen accountability - Identifies what should have been reported
• World-class comparison - Compares reporting quality to BBC, Reuters standards
• True Report generation - Shows how the article should have been written

📰 HOW IT WORKS:
1. Navigate to any news article
2. Click the extension icon
3. Click "Analyze This Article"
4. Extension extracts content and sends to News Checker app
5. Get comprehensive analysis in seconds

✅ BENEFITS:
• Bypass website blocking - Extracts content directly from browser
• No manual copying needed - Automatic content extraction
• Fast and reliable - Works on most news websites
• Free to use - No subscription required

🔒 PRIVACY:
• Content is only sent to your configured News Checker app
• No data is stored by the extension
• All analysis happens on the Streamlit server

Perfect for journalists, researchers, students, and anyone who wants to verify news credibility and understand media bias.
```

**Category:**
```
Productivity
```

### 4.2 Graphics

**Small Promotional Tile (440x280):**
- Create a promotional image showing the extension in action
- Include: Extension icon, "News Checker" text, "Fact-Check News Articles" tagline
- Use tools like Canva, Figma, or Photoshop

**Screenshots (1280x800 or 640x400):**
Create 1-5 screenshots showing:
1. Extension popup interface
2. Analysis results in Streamlit app
3. Extension icon in toolbar
4. Content extraction in action

**Promotional Images (Optional but Recommended):**
- Marquee Promotional Tile (920x680)
- Small Promotional Tile (440x280) - Required
- Large Promotional Tile (1400x560)

### 4.3 Privacy

**Single Purpose:**
```
Yes - The extension has a single purpose: to extract news article content and send it to the News Checker analysis service.
```

**Host Permissions:**
```
The extension requests "activeTab" permission to:
- Read the current page URL
- Extract article content from the page
- Send content to News Checker app for analysis

No data is collected or stored. Content is only sent to the user's configured Streamlit app URL.
```

**User Data:**
```
The extension does not collect, store, or transmit any personal data. It only:
- Reads the current page URL (with user permission)
- Extracts article content (text only)
- Sends content to the user's configured News Checker app URL

Users can configure their own Streamlit app URL. No data is sent to third parties.
```

### 4.4 Distribution

**Visibility:**
- Choose: **"Public"** (anyone can install) or **"Unlisted"** (only with link)

**Regions:**
- Select: **"All regions"** or specific countries

**Pricing:**
- **Free** (recommended)

## Step 5: Submit for Review

1. Review all information
2. Click **"Submit for Review"**
3. Wait for review (usually 1-3 business days)
4. Google will email you when approved/rejected

## Step 6: After Approval

1. Extension will be live on Chrome Web Store
2. Share the store link with users
3. Users can install with one click
4. Monitor reviews and ratings

## Store Listing Checklist

Before submitting, ensure:

- [ ] ZIP file contains only necessary files
- [ ] Manifest.json is valid
- [ ] Icons are present (16, 48, 128)
- [ ] Description is clear and accurate
- [ ] Screenshots are provided
- [ ] Privacy information is complete
- [ ] Extension works in test environment
- [ ] No errors in Chrome extension console

## Updating the Extension

When you need to update:

1. Update version in `manifest.json`
2. Create new ZIP file
3. Go to Chrome Web Store Developer Dashboard
4. Click on your extension
5. Click "Package" → "Upload new package"
6. Upload new ZIP
7. Submit for review (updates usually faster)

## Tips for Approval

1. **Clear Description**: Explain what the extension does
2. **Privacy First**: Be transparent about data usage
3. **Good Screenshots**: Show the extension in action
4. **Single Purpose**: Extension should have one clear purpose ✅
5. **No Malware**: Ensure no suspicious code
6. **User Permissions**: Only request necessary permissions ✅

## Common Rejection Reasons

- Missing or unclear privacy policy
- Vague description
- Poor screenshots
- Suspicious permissions
- Malware detected (false positives possible)
- Violates Chrome Web Store policies

## Support

If your extension is rejected:
1. Read the rejection reason carefully
2. Fix the issues mentioned
3. Resubmit with updated package
4. Contact Chrome Web Store support if needed

## Resources

- Chrome Web Store Developer Dashboard: https://chrome.google.com/webstore/devconsole
- Chrome Extension Documentation: https://developer.chrome.com/docs/extensions/
- Store Listing Guidelines: https://developer.chrome.com/docs/webstore/cws-dashboard-overview/


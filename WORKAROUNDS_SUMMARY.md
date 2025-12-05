# Workarounds for Blocked Websites - Quick Summary

When a website blocks automated access (401/403 errors), here are your options:

## ✅ **Currently Active (Auto-Tries)**

### 1. **Manual Content Paste** ⭐ RECOMMENDED
- **How**: Switch to "Paste Article Content" in the UI
- **Pros**: 100% reliable, works for any site, fastest
- **Cons**: Requires copying text manually
- **When to use**: Always works, especially for Reuters, Bloomberg, paywalled sites

### 2. **Newspaper3k Library** (Auto-tries)
- **Status**: ✅ Installed and auto-tries
- **Works for**: Many news sites (BBC, CNN, etc.)
- **Doesn't work for**: Reuters, Bloomberg (they block everything)

### 3. **RSS Feed Parsing** (Auto-tries)
- **Status**: ✅ Installed and auto-tries
- **Works for**: Sites with RSS feeds
- **Limitation**: May not have full article text

## 🔧 **Available but Require Setup**

### 4. **Selenium (Headless Browser)**
- **What**: Real browser automation
- **Installation**:
  ```bash
  pip install selenium
  brew install chromedriver  # Mac
  ```
- **Pros**: Bypasses many protections, handles JavaScript
- **Cons**: Slower, requires ChromeDriver
- **When to use**: JavaScript-heavy sites

### 5. **Playwright (Modern Browser)**
- **What**: Better alternative to Selenium
- **Installation**:
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Pros**: More reliable, better performance
- **Cons**: Requires browser download (~200MB)
- **When to use**: Modern sites with heavy JavaScript

## 📊 **What Happens Automatically**

When you enter a URL and it gets blocked:

1. ✅ System tries **Newspaper3k** automatically
2. ✅ System tries **RSS Feed** automatically  
3. ⚠️ Shows error with suggestions
4. 💡 You can then use **Manual Paste** (fastest solution)

## 🎯 **Recommended Workflow**

```
URL blocked?
    ↓
Try automatic fallbacks (happens automatically)
    ↓
Still blocked?
    ↓
Use Manual Paste (2 minutes, 100% reliable)
```

## 💡 **Quick Tips**

- **Reuters/Bloomberg**: Always use Manual Paste (they block everything)
- **Most news sites**: Automatic fallbacks often work
- **Paywalled articles**: Only Manual Paste works
- **JavaScript sites**: Need Selenium/Playwright (advanced)

## 🚀 **For Developers**

To enable browser automation in code, the functions are already there:
- `fetch_with_selenium(url)` 
- `fetch_with_playwright(url)`

Just install the dependencies and they'll work automatically.

## 📝 **Current Status**

✅ **Working Now**:
- Manual Paste (always available)
- Newspaper3k (auto-tries)
- RSS Feed (auto-tries)

⚠️ **Available but Need Setup**:
- Selenium (install ChromeDriver)
- Playwright (install browser)

---

**Bottom Line**: For blocked sites like Reuters, **Manual Paste is your best friend** - it's fast, reliable, and always works! 🎯


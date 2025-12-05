# Advanced Article Fetching - Workarounds for Blocked Sites

When websites block automated access (401/403 errors), here are multiple workarounds available:

## 🔧 Available Methods

### 1. **Newspaper3k Library** (Recommended First)
- **What it does**: Specialized library for news article extraction
- **Pros**: Handles many news sites, good content extraction
- **Cons**: May still be blocked by some sites
- **Installation**: Already in requirements.txt
- **Status**: ✅ Auto-tries as fallback

### 2. **RSS Feed Parsing**
- **What it does**: Looks for RSS feeds on the news site
- **Pros**: Often not blocked, structured data
- **Cons**: Not all sites have RSS, may not have full article
- **Status**: ✅ Auto-tries as fallback

### 3. **Selenium (Headless Browser)**
- **What it does**: Uses real browser automation to load JavaScript
- **Pros**: Bypasses many anti-bot protections, handles dynamic content
- **Cons**: Requires Chrome/Chromium, slower, more resource-intensive
- **Installation**: 
  ```bash
  pip install selenium
  # Also need ChromeDriver: brew install chromedriver (Mac) or download
  ```
- **Usage**: Enable in code when needed

### 4. **Playwright (Modern Browser Automation)**
- **What it does**: Modern alternative to Selenium, better performance
- **Pros**: More reliable, better at handling modern sites
- **Cons**: Requires browser installation, slower
- **Installation**:
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Usage**: Enable in code when needed

### 5. **Manual Content Paste** (Always Available)
- **What it does**: User copies and pastes article content
- **Pros**: 100% reliable, works for any site
- **Cons**: Requires manual work
- **Status**: ✅ Available in UI

## 🚀 How to Enable Browser Automation

### Option 1: Install Selenium
```bash
source venv/bin/activate
pip install selenium
# Install ChromeDriver
brew install chromedriver  # Mac
# or download from https://chromedriver.chromium.org/
```

Then uncomment Selenium code in `news_analyzer.py` (it's already there, just needs ChromeDriver).

### Option 2: Install Playwright
```bash
source venv/bin/activate
pip install playwright
playwright install chromium
```

## 📋 Current Auto-Fallback Order

When a site blocks access, the system automatically tries:

1. ✅ **Newspaper3k** - Fast, handles many sites
2. ✅ **RSS Feed** - Good for news sites with feeds
3. ⚠️ **Selenium** - Manual enable (requires setup)
4. ⚠️ **Playwright** - Manual enable (requires setup)
5. ✅ **Manual Paste** - Always available in UI

## 🎯 Recommended Approach

1. **First**: Let the system try automatic fallbacks (newspaper3k, RSS)
2. **If that fails**: Use manual paste in the UI (fastest, most reliable)
3. **For frequent use**: Set up Selenium/Playwright for JavaScript-heavy sites

## 💡 Tips

- **Reuters, Bloomberg, etc.**: Often block all automated access - use manual paste
- **Most news sites**: Newspaper3k or RSS feed work well
- **JavaScript-heavy sites**: Need Selenium/Playwright
- **Paywalled articles**: Manual paste is the only option

## 🔍 Testing Methods

You can test which method works:

```python
from news_analyzer import NewsAnalyzer

analyzer = NewsAnalyzer()

# Test newspaper3k
result = analyzer.fetch_with_newspaper3k(url)

# Test RSS
result = analyzer.try_rss_feed(url)

# Test Selenium (if installed)
result = analyzer.fetch_with_selenium(url)

# Test Playwright (if installed)
result = analyzer.fetch_with_playwright(url)
```

## ⚙️ Configuration

To enable browser automation for all requests, modify `fetch_article_content()` to include Selenium/Playwright in the fallback chain automatically.


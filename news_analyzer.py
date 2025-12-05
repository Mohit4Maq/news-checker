"""
News Analyzer - Fact-checking and propaganda detection system
Uses OpenAI API to analyze news articles based on comprehensive rules
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import feedparser
import time
from urllib.parse import urlparse, urljoin

# Optional imports for advanced scraping
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

# Load environment variables
load_dotenv()

class NewsAnalyzer:
    """Main class for analyzing news articles"""
    
    def __init__(self):
        """Initialize the analyzer with OpenAI client"""
        # Try to get API key from Streamlit secrets first (for Streamlit Cloud)
        # Then fall back to environment variable (for local development)
        try:
            import streamlit as st
            api_key = st.secrets.get("OPEN_AI_API", "")
        except:
            api_key = os.getenv("OPEN_AI_API", "").strip('"')
        
        if not api_key:
            raise ValueError("OPENAI_API key not found. Please set OPEN_AI_API in Streamlit secrets or .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.rules_path = "NEWS_ANALYSIS_RULES.md"
        self.model = "gpt-4o"  # Default model, will be updated by test_api_key
        
    def test_api_key(self) -> bool:
        """Test if the OpenAI API key is working"""
        # Try different models in order of preference
        models_to_try = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "Say OK"}
                    ],
                    max_tokens=5
                )
                self.model = model  # Store working model
                return True  # If we got a response, API key works
            except Exception as e:
                if model == models_to_try[-1]:  # Last model
                    print(f"API Key Test Failed with all models. Last error: {str(e)}")
                continue
        return False
    
    def fetch_with_newspaper3k(self, url: str) -> Dict[str, Any]:
        """Try fetching using newspaper3k library (handles many news sites)"""
        if not NEWSPAPER_AVAILABLE:
            return {"success": False, "error": "newspaper3k not installed"}
        
        try:
            article = Article(url, language='en')
            # Set longer timeout for Streamlit Cloud
            article.config.request_timeout = 20
            article.config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
            article.download()
            article.parse()
            
            # Lower threshold - accept if we have any reasonable content
            if article.text and len(article.text.strip()) > 50:
                return {
                    "success": True,
                    "title": article.title or "No title found",
                    "content": article.text.strip(),
                    "url": url,
                    "method": "newspaper3k"
                }
        except Exception as e:
            # Don't return error immediately - might still work with other methods
            pass
        return {"success": False, "error": "newspaper3k failed to extract content"}
    
    def fetch_with_selenium(self, url: str) -> Dict[str, Any]:
        """Try fetching using Selenium (handles JavaScript-heavy sites)"""
        if not SELENIUM_AVAILABLE:
            return {"success": False, "error": "selenium not installed"}
        
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for content to load
            time.sleep(3)
            
            # Try to find and close cookie/consent banners
            try:
                close_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Close') or contains(text(), '×')]")
                for btn in close_buttons[:3]:  # Try first 3
                    try:
                        btn.click()
                        time.sleep(1)
                    except:
                        pass
            except:
                pass
            
            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract title
            title = driver.title or soup.find('title')
            title_text = title if isinstance(title, str) else (title.get_text().strip() if title else "No title found")
            
            # Extract content
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            article_content = None
            content_selectors = ['article', '[role="article"]', '.article-content', '.article-body', 'main']
            for selector in content_selectors:
                article = soup.select_one(selector)
                if article:
                    article_content = article.get_text(separator='\n', strip=True)
                    if len(article_content) > 200:
                        break
            
            if not article_content:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    article_content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            
            if article_content and len(article_content) > 100:
                return {
                    "success": True,
                    "title": title_text,
                    "content": article_content[:5000],  # Limit content
                    "url": url,
                    "method": "selenium"
                }
        except Exception as e:
            return {"success": False, "error": f"selenium error: {str(e)}"}
        finally:
            if driver:
                driver.quit()
        return {"success": False, "error": "selenium failed to extract content"}
    
    def fetch_with_playwright(self, url: str) -> Dict[str, Any]:
        """Try fetching using Playwright (modern headless browser)"""
        if not PLAYWRIGHT_AVAILABLE:
            return {"success": False, "error": "playwright not installed"}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Get content
                title = page.title()
                content = page.content()
                
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                article_content = None
                content_selectors = ['article', '[role="article"]', '.article-content', '.article-body', 'main']
                for selector in content_selectors:
                    article = soup.select_one(selector)
                    if article:
                        article_content = article.get_text(separator='\n', strip=True)
                        if len(article_content) > 200:
                            break
                
                if not article_content:
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        article_content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                if article_content and len(article_content) > 100:
                    return {
                        "success": True,
                        "title": title or "No title found",
                        "content": article_content[:5000],
                        "url": url,
                        "method": "playwright"
                    }
        except Exception as e:
            return {"success": False, "error": f"playwright error: {str(e)}"}
        return {"success": False, "error": "playwright failed to extract content"}
    
    def try_rss_feed(self, url: str) -> Dict[str, Any]:
        """Try to find and parse RSS feed for the article"""
        # Extract base domain
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Common RSS feed paths
            rss_paths = ['/feed', '/rss', '/feeds/all.rss', '/rss.xml', '/feed.xml']
            
            for path in rss_paths:
                try:
                    feed_url = base_url + path
                    feed = feedparser.parse(feed_url)
                    
                    if feed.entries:
                        # Try to find matching article
                        for entry in feed.entries[:10]:  # Check first 10 entries
                            if url in entry.get('link', '') or entry.get('link', '') in url:
                                return {
                                    "success": True,
                                    "title": entry.get('title', 'No title'),
                                    "content": entry.get('summary', '') or entry.get('description', ''),
                                    "url": url,
                                    "method": "rss_feed"
                                }
                except:
                    continue
        except Exception as e:
            pass
        return {"success": False, "error": "RSS feed not found or doesn't contain article"}
    
    def find_related_articles(self, url: str, current_title: str, current_content: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Find related articles from the same website"""
        try:
            
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            related_articles = []
            
            # Extract keywords from title and content
            title_words = set(re.findall(r'\b\w{4,}\b', current_title.lower()))
            content_words = set(re.findall(r'\b\w{5,}\b', current_content.lower()[:500]))
            keywords = list(title_words.union(content_words))[:10]  # Top 10 keywords
            
            # Try to find related articles via RSS feed
            try:
                rss_paths = ['/feed', '/rss', '/feeds/all.rss', '/rss.xml', '/feed.xml']
                for path in rss_paths:
                    try:
                        feed_url = base_url + path
                        feed = feedparser.parse(feed_url)
                        
                        if feed.entries:
                            for entry in feed.entries[:20]:  # Check more entries
                                entry_url = entry.get('link', '')
                                entry_title = entry.get('title', '').lower()
                                entry_summary = (entry.get('summary', '') or entry.get('description', '')).lower()
                                
                                # Skip if it's the same article
                                if entry_url == url or url in entry_url:
                                    continue
                                
                                # Check relevance by keyword matching
                                relevance_score = 0
                                entry_text = entry_title + " " + entry_summary
                                
                                for keyword in keywords:
                                    if keyword in entry_text:
                                        relevance_score += 1
                                
                                # Also check for common topics (India, Modi, Putin, etc.)
                                common_topics = ['india', 'modi', 'putin', 'russia', 'diplomatic', 'visit', 'policy']
                                for topic in common_topics:
                                    if topic in entry_text and topic in current_content.lower():
                                        relevance_score += 2
                                
                                if relevance_score >= 2:  # Minimum relevance threshold
                                    related_articles.append({
                                        "url": entry_url,
                                        "title": entry.get('title', 'No title'),
                                        "summary": entry.get('summary', '') or entry.get('description', ''),
                                        "relevance_score": relevance_score,
                                        "published": entry.get('published', ''),
                                        "source": "rss_feed"
                                    })
                                    
                                    if len(related_articles) >= max_articles:
                                        break
                        
                        if len(related_articles) >= max_articles:
                            break
                    except:
                        continue
            except:
                pass
            
            # Try to fetch related articles from the same page (if article page has "related articles" section)
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for related articles links
                    related_selectors = [
                        'a[href*="related"]',
                        '.related-articles a',
                        '.more-articles a',
                        '.similar-articles a',
                        '[class*="related"] a',
                        '[class*="similar"] a'
                    ]
                    
                    for selector in related_selectors:
                        links = soup.select(selector)
                        for link in links[:10]:
                            href = link.get('href', '')
                            if href:
                                if not href.startswith('http'):
                                    href = urljoin(base_url, href)
                                
                                if href != url and base_url in href:
                                    title = link.get_text(strip=True)
                                    if title and len(title) > 10:
                                        # Check relevance
                                        title_lower = title.lower()
                                        relevance = sum(1 for kw in keywords if kw in title_lower)
                                        
                                        if relevance >= 1:
                                            related_articles.append({
                                                "url": href,
                                                "title": title,
                                                "summary": "",
                                                "relevance_score": relevance,
                                                "source": "page_links"
                                            })
                                            
                                            if len(related_articles) >= max_articles:
                                                break
                        
                        if len(related_articles) >= max_articles:
                            break
            except:
                pass
            
            # Sort by relevance score and return top articles
            related_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return related_articles[:max_articles]
            
        except Exception as e:
            return []
    
    def analyze_related_articles(self, current_article: Dict[str, Any], related_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze related articles and compare with current article"""
        if not related_articles:
            return {
                "related_articles_found": False,
                "message": "No related articles found on the same website"
            }
        
        analysis = {
            "related_articles_found": True,
            "total_found": len(related_articles),
            "articles": []
        }
        
        current_title = current_article.get('title', '').lower()
        current_content = current_article.get('content', '').lower()
        
        for article in related_articles:
            article_analysis = {
                "url": article.get('url', ''),
                "title": article.get('title', ''),
                "relevance_score": article.get('relevance_score', 0),
                "summary": article.get('summary', '')[:200] if article.get('summary') else "",
                "comparison": {}
            }
            
            article_title = article.get('title', '').lower()
            article_summary = (article.get('summary', '') or '').lower()
            
            # Compare topics
            current_topics = set(re.findall(r'\b\w{5,}\b', current_content[:1000]))
            article_topics = set(re.findall(r'\b\w{5,}\b', article_summary[:1000]))
            
            common_topics = current_topics.intersection(article_topics)
            unique_to_current = current_topics - article_topics
            unique_to_related = article_topics - current_topics
            
            article_analysis["comparison"] = {
                "common_topics": list(common_topics)[:5],
                "topics_in_related_not_in_current": list(unique_to_related)[:5],
                "topics_in_current_not_in_related": list(unique_to_current)[:5]
            }
            
            # Try to fetch full content for deeper analysis
            try:
                fetched = self.fetch_article_content(article.get('url', ''), use_fallbacks=False)
                if fetched.get('success'):
                    article_analysis["full_content_available"] = True
                    article_analysis["content_length"] = len(fetched.get('content', ''))
                    
                    # More detailed comparison
                    related_content = fetched.get('content', '').lower()
                    
                    # Find what's in related article but missing in current
                    related_sentences = [s.strip() for s in related_content.split('.') if len(s.strip()) > 50]
                    current_sentences = [s.strip() for s in current_content.split('.') if len(s.strip()) > 50]
                    
                    # Find unique information in related article
                    unique_info = []
                    for rel_sent in related_sentences[:20]:
                        if not any(rel_sent[:50] in curr_sent for curr_sent in current_sentences):
                            # Check if it contains important keywords
                            if any(kw in rel_sent for kw in ['policy', 'security', 'impact', 'citizen', 'government', 'cost', 'benefit']):
                                unique_info.append(rel_sent[:150])
                                if len(unique_info) >= 3:
                                    break
                    
                    article_analysis["comparison"]["information_in_related_not_in_current"] = unique_info
                else:
                    article_analysis["full_content_available"] = False
            except:
                article_analysis["full_content_available"] = False
            
            analysis["articles"].append(article_analysis)
        
        return analysis
    
    def fetch_article_content(self, url: str, use_fallbacks: bool = True) -> Dict[str, Any]:
        """Fetch and extract content from a news URL with multiple fallback methods"""
        
        # Try newspaper3k FIRST (works better on Streamlit Cloud for many sites)
        if use_fallbacks:
            print("   Trying newspaper3k first (best for Streamlit Cloud)...")
            newspaper_result = self.fetch_with_newspaper3k(url)
            if newspaper_result.get("success") and len(newspaper_result.get("content", "")) > 100:
                return newspaper_result
        
        # Comprehensive headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            # Try with session first
            response = session.get(url, timeout=20, allow_redirects=True)
            
            # Handle common error codes
            if response.status_code == 401:
                # Try fallback methods for 401 errors
                if use_fallbacks:
                    print(f"   401 Forbidden - trying fallback methods...")
                    fallback_methods = [
                        ("newspaper3k", self.fetch_with_newspaper3k),
                        ("RSS feed", self.try_rss_feed),
                    ]
                    
                    for method_name, method_func in fallback_methods:
                        print(f"   Trying: {method_name}...")
                        result = method_func(url)
                        if result.get("success"):
                            return result
                
                return {
                    "success": False,
                    "error": f"401 Forbidden: This website requires authentication or blocks automated access.",
                    "url": url,
                    "suggestion": "Options: 1) Use browser automation (Selenium/Playwright), 2) Try newspaper3k library, 3) Check RSS feed, 4) Copy article content manually."
                }
            elif response.status_code == 403:
                # Try fallback methods for 403 errors
                if use_fallbacks:
                    print(f"   403 Forbidden - trying fallback methods...")
                    fallback_methods = [
                        ("newspaper3k", self.fetch_with_newspaper3k),
                        ("RSS feed", self.try_rss_feed),
                    ]
                    
                    # Only try browser automation if other methods fail (slower)
                    for method_name, method_func in fallback_methods:
                        print(f"   Trying: {method_name}...")
                        result = method_func(url)
                        if result.get("success"):
                            return result
                
                return {
                    "success": False,
                    "error": f"403 Forbidden: Access denied. This website may block automated requests.",
                    "url": url,
                    "suggestion": "This site blocks automated access. Options: 1) Use browser automation (Selenium/Playwright), 2) Try newspaper3k library, 3) Check for RSS feed, 4) Copy article content manually."
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"404 Not Found: The article URL doesn't exist or has been removed.",
                    "url": url
                }
            
            response.raise_for_status()
            
            # Try to detect encoding
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Extract title (try multiple methods)
            title_text = "No title found"
            title_selectors = [
                ('meta', {'property': 'og:title'}),
                ('meta', {'name': 'twitter:title'}),
                ('h1', {}),
                ('title', {})
            ]
            
            for tag, attrs in title_selectors:
                element = soup.find(tag, attrs) if attrs else soup.find(tag)
                if element:
                    title_text = element.get('content') or element.get_text()
                    if title_text and title_text.strip():
                        title_text = title_text.strip()
                        break
            
            # Extract main content (try common article selectors - EXPANDED LIST)
            article_content = None
            content_selectors = [
                'article',
                '[role="article"]',
                '.article-content',
                '.article-body',
                '.post-content',
                '.story-body',
                '.content-body',
                '.entry-content',
                '.post-body',
                '.article-text',
                '.article-main',
                '.story-content',
                '.article-wrapper',
                '.content-wrapper',
                '[class*="article"]',
                '[class*="story"]',
                '[class*="content"]',
                '[class*="post"]',
                '[class*="entry"]',
                'main',
                '.main-content',
                '#main-content',
                '#article-content',
                '#story-content',
                '[id*="article"]',
                '[id*="content"]',
                '[id*="story"]'
            ]
            
            for selector in content_selectors:
                try:
                    article = soup.select_one(selector)
                    if article:
                        # Get text but preserve some structure
                        article_content = article.get_text(separator='\n', strip=True)
                        # Lower threshold - accept if we have reasonable content
                        if len(article_content) > 150:
                            break
                except:
                    continue
            
            if not article_content or len(article_content) < 150:
                # Try multiple paragraph extraction strategies
                paragraphs = soup.find_all('p')
                if paragraphs:
                    para_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20]
                    if para_texts:
                        article_content = '\n'.join(para_texts)
            
            if not article_content or len(article_content) < 100:
                # Try divs with text content
                divs = soup.find_all('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower() or 'story' in x.lower()))
                if divs:
                    div_texts = []
                    for div in divs:
                        text = div.get_text(separator='\n', strip=True)
                        if len(text) > 100:
                            div_texts.append(text)
                    if div_texts:
                        # Use the longest div
                        article_content = max(div_texts, key=len)
            
            if not article_content or len(article_content) < 80:
                # Last resort: get body text but filter out navigation/menu items
                body = soup.find('body')
                if body:
                    # Remove common non-content elements
                    for elem in body.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                        elem.decompose()
                    article_content = body.get_text(separator='\n', strip=True)
            
            # Lower threshold - accept content if we have at least 80 characters
            if not article_content or len(article_content) < 80:
                # Try fallback methods if enabled (more aggressively)
                if use_fallbacks:
                    fallback_methods = [
                        ("newspaper3k", self.fetch_with_newspaper3k),
                        ("RSS feed", self.try_rss_feed),
                    ]
                    
                    for method_name, method_func in fallback_methods:
                        print(f"   Trying fallback: {method_name}...")
                        result = method_func(url)
                        if result.get("success"):
                            # Accept even if content is shorter than ideal
                            content = result.get("content", "")
                            if content and len(content) > 50:
                                return result
                
                # If we got SOME content but it's short, still return it
                if article_content and len(article_content) >= 50:
                    # Clean up the content
                    lines = [line.strip() for line in article_content.split('\n') if line.strip() and len(line.strip()) > 10]
                    article_content = '\n'.join(lines[:100])  # Limit to first 100 paragraphs
                    
                    return {
                        "success": True,
                        "title": title_text,
                        "content": article_content,
                        "url": url,
                        "content_length": len(article_content),
                        "method": "requests (partial extraction)",
                        "warning": "Content may be incomplete - consider manual paste for full article"
                    }
                
                return {
                    "success": False,
                    "error": "Could not extract sufficient content from the article. The page structure may not be supported.",
                    "url": url,
                    "suggestion": "Try copying the article content manually, use browser automation (Selenium/Playwright), or use a different news source."
                }
            
            # Clean up the content - be more lenient with filtering
            lines = [line.strip() for line in article_content.split('\n') if line.strip() and len(line.strip()) > 5]
            # Remove very short lines that are likely navigation/menu items
            filtered_lines = []
            for line in lines:
                # Skip lines that look like navigation (short, all caps, or common menu items)
                if len(line) > 8 and not (line.isupper() and len(line) < 30):
                    filtered_lines.append(line)
            
            article_content = '\n'.join(filtered_lines[:200])  # Limit to first 200 paragraphs
            
            # If content is still substantial, return success
            if len(article_content) >= 80:
                return {
                    "success": True,
                    "title": title_text,
                    "content": article_content,
                    "url": url,
                    "content_length": len(article_content),
                    "method": "requests"
                }
            else:
                # Content too short, try fallbacks
                if use_fallbacks:
                    fallback_methods = [
                        ("newspaper3k", self.fetch_with_newspaper3k),
                        ("RSS feed", self.try_rss_feed),
                    ]
                    
                    for method_name, method_func in fallback_methods:
                        print(f"   Trying fallback: {method_name}...")
                        result = method_func(url)
                        if result.get("success"):
                            content = result.get("content", "")
                            if content and len(content) > 50:
                                return result
                
                # Return partial content if we have something
                if article_content and len(article_content) >= 50:
                    return {
                        "success": True,
                        "title": title_text,
                        "content": article_content,
                        "url": url,
                        "content_length": len(article_content),
                        "method": "requests (partial)",
                        "warning": "Content may be incomplete"
                    }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. The website may be slow or unreachable.",
                "url": url
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error. Please check your internet connection.",
                "url": url
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.response.status_code}: {str(e)}",
                "url": url,
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching article: {str(e)}",
                "url": url
            }
    
    def load_rules(self) -> str:
        """Load the news analysis rules document"""
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load rules file: {e}")
            return ""
    
    def refine_category_based_on_scores(self, analysis: Dict[str, Any], article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine category based on individual section scores and article keywords"""
        if not isinstance(analysis, dict):
            return analysis
        
        # Extract scores
        fa_score = analysis.get("factual_accuracy", {}).get("score", 0)
        sc_score = analysis.get("source_credibility", {}).get("score", 0)
        bl_score = analysis.get("bias_level", {}).get("score", 0)
        pi_score = analysis.get("propaganda_indicators", {}).get("score", 0)
        ir_score = analysis.get("india_relevance", {}).get("score", 0)
        overall_score = analysis.get("overall_score", 0)
        
        # Extract keywords from article
        article_title = article_data.get("title", "").lower()
        article_content = article_data.get("content", "").lower()
        
        # Find key terms
        key_terms = []
        important_terms = ['modi', 'putin', 'russia', 'diplomatic', 'security', 'policy', 'economic', 
                          'government', 'citizen', 'india', 'visit', 'meeting', 'agreement', 'deal']
        for term in important_terms:
            if term in article_title or term in article_content[:500]:
                key_terms.append(term.title())
        
        # Determine category based on scores
        category = analysis.get("category", "UNKNOWN")
        category_keywords = analysis.get("category_keywords", key_terms[:3])
        category_reasoning = analysis.get("category_reasoning", "")
        
        # Refine category logic
        if fa_score < 15 and sc_score < 10:
            if pi_score < 8 or bl_score < 8:
                if overall_score < 45:
                    category = f"Propaganda - {category_keywords[0] if category_keywords else 'Agenda-Driven'} Content" if category_keywords else "PROPAGANDA"
                else:
                    category = f"Misinformation - {category_keywords[0] if category_keywords else 'Unverified'} Claims" if category_keywords else "MISINFORMATION"
            else:
                category = f"Incomplete Reporting - Missing {category_keywords[0] if category_keywords else 'Critical'} Information" if category_keywords else "MISINFORMATION"
        elif fa_score >= 20 and sc_score >= 15:
            if pi_score >= 12 and bl_score >= 10:
                category = f"Factual News - {category_keywords[0] if category_keywords else 'Verified'} Reporting" if category_keywords else "FACTUAL NEWS"
            else:
                category = f"Factual but {category_keywords[0] if category_keywords else 'Biased'} - Needs Balance" if category_keywords else "FACTUAL NEWS"
        elif overall_score >= 60 and fa_score >= 15:
            category = f"Likely Factual - {category_keywords[0] if category_keywords else 'Verified'} with Gaps" if category_keywords else "FACTUAL NEWS"
        elif overall_score < 60 and overall_score >= 45:
            category = f"Questionable - {category_keywords[0] if category_keywords else 'Unverified'} Information" if category_keywords else "MISINFORMATION"
        elif overall_score < 45:
            if pi_score < 8:
                category = f"Propaganda - {category_keywords[0] if category_keywords else 'Manipulative'} Content" if category_keywords else "PROPAGANDA"
            else:
                category = f"Severe Misinformation - {category_keywords[0] if category_keywords else 'False'} Claims" if category_keywords else "MISINFORMATION"
        
        # Update category reasoning if not provided
        if not category_reasoning:
            reasons = []
            if fa_score < 15:
                reasons.append("low factual accuracy")
            if sc_score < 10:
                reasons.append("poor source credibility")
            if pi_score < 8:
                reasons.append("propaganda indicators")
            if bl_score < 8:
                reasons.append("high bias")
            category_reasoning = f"Category determined by: {', '.join(reasons) if reasons else 'overall assessment'}"
        
        # Update analysis
        analysis["category"] = category
        analysis["category_keywords"] = category_keywords
        analysis["category_reasoning"] = category_reasoning
        
        return analysis
    
    def create_condensed_rules(self, full_rules: str) -> str:
        """Create a condensed version of rules focusing on key criteria"""
        # Extract key sections from the rules
        condensed = """
# NEWS ANALYSIS RULES - KEY CRITERIA

## PROPAGANDA INDICATORS
1. Emotional Manipulation: Excessive loaded language, fear-mongering, sensational headlines
2. Source Issues: Anonymous/unverifiable sources, single source dependency, misattributed quotes
3. Logical Fallacies: Ad hominem, false dichotomies, strawman arguments, cherry-picking
4. Bias: One-sided presentation, omission of key facts, false balance
5. Agenda-Driven: Political alignment, commercial interests, religious/communal angle, foreign influence
6. Factual Distortions: Outdated info, geographic misrepresentation, number manipulation

## FACTUAL NEWS CRITERIA
1. Source Verification: Multiple independent sources, primary sources, reputable organizations
2. Transparency: Clear attribution, methodology disclosure, correction policy
3. Balance: Multiple perspectives, historical context, nuanced analysis
4. Journalistic Standards: Fact-checking, editorial oversight, ethical guidelines

## SCORING SYSTEM (0-100 points)
- Factual Accuracy: 0-30 points (verification, multiple sources)
- Source Credibility: 0-20 points (reputation, verification)
- Bias Level: 0-15 points (minimal bias = high score)
- Propaganda Indicators: 0-15 points (no indicators = high score)
- India Relevance: 0-20 points (direct impact = high score)

## CATEGORIES
- FACTUAL NEWS: Score 75-100, verified, credible, balanced
- PROPAGANDA: Score 0-44, agenda-driven, manipulative
- MISINFORMATION: Score 45-59, false/unverified info
- OPINION/ANALYSIS: Clearly labeled opinion
- SATIRE/PARODY: Humorous content

## INDIA-SPECIFIC RELEVANCE
High Relevance (15-20): Direct impact on policy, economy, society, security affecting majority
Medium Relevance (8-14): Regional/sectoral impact, significant portion affected
Low Relevance (1-7): Specific groups, minimal policy impact
No Relevance (0): No connection to India

## ANALYSIS REQUIREMENTS
Provide detailed reasoning with specific examples from the article for each score.
"""
        return condensed
    
    def create_analysis_prompt(self, article_data: Dict[str, Any], rules: str, use_condensed: bool = True) -> str:
        """Create the prompt for OpenAI analysis with critical questioning approach"""
        # Use condensed rules if the full rules are too long
        if use_condensed and len(rules) > 10000:
            rules = self.create_condensed_rules(rules)
        
        prompt = f"""You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is NOT to accept what's reported at face value, but to QUESTION EVERYTHING, identify what's MISSING, and demand ANSWERS that Indian citizens deserve.

CRITICAL ANALYSIS FRAMEWORK:
1. DON'T just report what the article says - QUESTION it
2. Ask: What questions should Indian citizens be asking?
3. Identify: What's NOT being said? What's being omitted?
4. Challenge: What's the other side of this story?
5. Demand: What answers does the report provide vs. what it should provide?
6. Judge: Based on what answers ARE provided, how credible is this?

Use the following rules document for reference:

{rules}

---

NEWS ARTICLE TO ANALYZE:

Title: {article_data.get('title', 'N/A')}
URL: {article_data.get('url', 'N/A')}

Content:
{article_data.get('content', 'N/A')}

---

CRITICAL QUESTIONING ANALYSIS - ACT AS OPPOSITION REPORTER:

**STEP 1: QUESTION THE NARRATIVE**
- What is this article REALLY trying to say? What's the hidden message?
- What questions does it raise but doesn't answer?
- What should Indian citizens be questioning about this story?
- What's the agenda here? Who benefits from this narrative?

**STEP 2: IDENTIFY WHAT'S MISSING**
- What crucial information is NOT provided?
- What sources are NOT quoted? What perspectives are missing?
- What questions should have been asked but weren't?
- What context is missing that Indian citizens need to understand this?

**STEP 3: CHALLENGE THE CLAIMS**
- Can each claim be verified? How?
- What evidence is provided vs. what should be provided?
- Are there alternative explanations that aren't explored?
- What would an opposition viewpoint say about this?

**STEP 3.5: BENEFICIARY & HIDDEN AGENDA ANALYSIS (CRITICAL)**
- **Who are the people/entities involved?** List everyone mentioned in the news
- **Who directly benefits?** Who gains from this news being reported this way?
- **Who indirectly benefits?** Who gains even though not mentioned?
- **What connections exist?** 
  * Media ownership connections to people involved
  * Business relationships between subjects
  * Political affiliations and party connections
  * Financial interests and investments
  * Family/personal relationships
- **What's the real news being hidden?** What important story is this obscuring?
- **Why this timing?** Why is this being reported now? What else is happening?
- **Conflict of interest check:** Do people involved have undisclosed stakes?
- **Agenda masking:** Is this story masking a bigger, more important issue?
- **Distraction analysis:** What is this news distracting citizens from?

**STEP 4: DEMAND ANSWERS FROM THE REPORT**
- What specific questions should Indian citizens ask about this?
- Does the report answer these questions? If not, why not?
- What information is presented as fact but is actually unverified?
- What should the reporter have asked but didn't?

**STEP 5: JUDGE BASED ON ANSWERS PROVIDED & SCORES**
- Given what answers ARE in the report, how credible is it?
- What's the gap between what citizens need to know vs. what's reported?
- Is this propaganda, factual news, or something in between?
- How does this serve or harm Indian citizens' right to information?
- **CATEGORIZATION RULES**: 
  * Use the INDIVIDUAL SECTION SCORES to determine category, NOT just overall score
  * If Factual Accuracy < 15/30 AND Source Credibility < 10/20 → Likely MISINFORMATION or PROPAGANDA
  * If Propaganda Indicators < 8/15 AND Bias Level < 8/15 → Likely PROPAGANDA
  * If Factual Accuracy > 20/30 AND Source Credibility > 15/20 → Likely FACTUAL NEWS
  * If overall score 45-59 with low factual accuracy → MISINFORMATION
  * If overall score 0-44 with high propaganda indicators → PROPAGANDA
  * If clearly opinion/analysis labeled → OPINION/ANALYSIS
  * Use SPECIFIC KEYWORDS from the article in the category name (e.g., "Symbolic Diplomatic Coverage - Incomplete Reporting" instead of just "MISINFORMATION")
  * Make category descriptive and specific to what the article actually is

**STEP 6: INDIA-SPECIFIC CRITICAL ANALYSIS**
- How does this REALLY affect ordinary Indian citizens? (Not just what it says, but what it means)
- What should citizens be concerned about that the article doesn't address?
- What's the real impact on policy, economy, society, or democracy?
- Is this relevant to citizens or just political theater?

**STEP 7: CITIZEN ACCOUNTABILITY - WHAT SHOULD HAVE BEEN REPORTED**
- What questions should Indian citizens be asking about this story?
- What topics should the article have covered for better accountability?
- What information do citizens NEED to know that the article doesn't provide?
- What would serve citizens' right to information and democratic accountability?
- What should the article have investigated or questioned?
- What are the real implications for citizens' lives, rights, or interests?
- What transparency or accountability issues should have been addressed?

**STEP 8: WORLD-CLASS REPORTING COMPARISON**

Compare this article's reporting quality against world's best news organizations (BBC, Reuters, The Guardian, New York Times, Washington Post, etc.) across key dimensions:
- Factual accuracy and verification standards
- Source diversity and credibility
- Balance and multiple perspectives
- Depth of investigation
- Transparency and accountability
- Citizen-focused reporting
- Context and background provided
- Data and evidence usage
- Expert consultation
- Independence from agenda

Rate this article (0-100) compared to world-class standards in each category.

**STEP 9: CREATE THE TRUE REPORT - HOW IT SHOULD HAVE BEEN REPORTED**

Based on ALL the questions, missing topics, and accountability gaps identified in the Citizen Accountability section, create a COMPLETE, UNBIASED, COMPREHENSIVE news report that serves Indian citizens properly.

The True Report MUST:
1. **Cover EVERY topic** identified in "topics_should_have_covered"
2. **Answer EVERY question** from "questions_citizens_should_ask"
3. **Include ALL information** from "information_citizens_need"
4. **Address ALL accountability gaps** identified
5. **Cover ALL transparency issues** raised
6. **Investigate ALL items** from "what_should_have_been_investigated"
7. **Focus on REAL citizen impact** not just surface-level reporting

The report should be:
- **Comprehensive**: Cover all aspects, not just one angle
- **Unbiased**: Multiple perspectives, balanced reporting
- **Well-sourced**: Primary sources, experts, official data, independent verification
- **Context-rich**: Historical context, policy background, precedents
- **Citizen-focused**: What matters to ordinary Indian citizens
- **Accountable**: Addresses transparency, accountability, democratic values
- **Factual**: Verifiable claims with proper evidence
- **Complete**: Nothing important left out

Structure the report with:
- Proper headline that captures the real story
- Lead paragraph that sets context for citizens
- Multiple sections covering all identified topics
- Expert opinions and analysis
- Data, statistics, and verifiable facts
- Multiple perspectives (government, opposition, experts, citizens)
- Policy implications and accountability aspects
- Real impact on citizens' lives and rights
- Proper sources and references for everything

---

SCORING WITH CRITICAL LENS:

1. **Factual Accuracy (0-30 points)** - Based on what CAN be verified from the report:
   - What claims are verifiable? What claims are NOT?
   - Does the report provide enough information to verify claims?
   - What's presented as fact but is actually speculation/opinion?
   - Score LOW if report doesn't provide verifiable evidence

2. **Source Credibility (0-20 points)** - Question the sources:
   - Are sources named? Are they credible? Are they independent?
   - What sources are MISSING? Why aren't opposing views included?
   - Are sources being used to push an agenda?
   - Score LOW if sources are anonymous, unverifiable, or one-sided

3. **Bias Level (0-15 points)** - Identify the bias:
   - What perspective is being pushed? What perspective is missing?
   - Is this one-sided? Who benefits from this narrative?
   - What would a balanced report look like?
   - Score LOW if clearly biased, one-sided, or agenda-driven

4. **Propaganda Indicators (0-15 points)** - Detect manipulation:
   - Is this trying to manipulate emotions? How?
   - What logical fallacies are present?
   - Is this designed to distract from real issues?
   - Score LOW if clear propaganda, emotional manipulation, or agenda-pushing

5. **India Relevance (0-20 points)** - Real impact on citizens:
   - Does this REALLY matter to ordinary Indian citizens? How?
   - What's the actual impact vs. what's claimed?
   - Is this relevant or just noise?
   - Score based on REAL relevance, not claimed relevance

---

Provide your CRITICAL ANALYSIS in the following JSON format:
{{
    "critical_questions": {{
        "questions_raised": ["<list of critical questions that should be asked>"],
        "questions_answered": ["<list of questions the report DOES answer>"],
        "questions_unanswered": ["<list of questions the report FAILS to answer>"],
        "missing_perspectives": ["<what perspectives/voices are missing>"],
        "hidden_agenda": "<what agenda might be behind this report>"
    }},
    "beneficiary_analysis": {{
        "people_involved": ["<list of all people, organizations, companies, parties mentioned>"],
        "direct_beneficiaries": ["<who directly benefits from this news being reported this way>"],
        "indirect_beneficiaries": ["<who indirectly benefits (not mentioned but gains)>"],
        "political_beneficiaries": ["<who gains politically from this narrative>"],
        "economic_beneficiaries": ["<who gains financially from this news>"],
        "reputational_beneficiaries": ["<whose image/reputation is improved>"],
        "connections_and_relationships": {{
            "media_connections": ["<connections between news subjects and media owners>"],
            "business_relationships": ["<business connections between people involved>"],
            "political_affiliations": ["<political party connections>"],
            "financial_interests": ["<financial stakes and investments>"],
            "undisclosed_relationships": ["<hidden connections that should be disclosed>"]
        }},
        "conflict_of_interest": ["<conflicts of interest that exist but aren't disclosed>"],
        "real_news_hidden": "<what important news is being obscured or hidden by this story>",
        "agenda_masking": "<what bigger story or issue is this masking/distracting from>",
        "timing_analysis": "<why is this being reported now? what else is happening?>",
        "distraction_purpose": "<what is this news distracting citizens from?>",
        "hidden_beneficiaries": ["<beneficiaries that are not mentioned in the article>"],
        "who_loses": ["<who stands to lose if the real story comes out>"]
    }},
    "factual_accuracy": {{
        "score": <0-30>,
        "reasoning": "<CRITICAL assessment - what CAN be verified vs. what CAN'T>",
        "verifiable_claims": ["<claims that CAN be verified from the report>"],
        "unverified_claims": ["<claims presented as fact but CANNOT be verified>"],
        "missing_evidence": ["<what evidence is missing that should be there>"]
    }},
    "source_credibility": {{
        "score": <0-20>,
        "reasoning": "<CRITICAL assessment - question the sources>",
        "sources_found": ["<list of sources mentioned>"],
        "sources_missing": ["<what sources SHOULD have been included but weren't>"],
        "credibility_assessment": "<are sources independent? credible? agenda-driven?>",
        "one_sided": "<yes/no - are opposing views included?>"
    }},
    "bias_level": {{
        "score": <0-15>,
        "reasoning": "<CRITICAL assessment - what bias is present>",
        "bias_types": ["<list of bias types detected>"],
        "examples": ["<specific examples of bias>"],
        "missing_balance": "<what would balance this report?>"
    }},
    "propaganda_indicators": {{
        "score": <0-15>,
        "reasoning": "<CRITICAL assessment - detect manipulation>",
        "indicators_found": ["<list of propaganda indicators>"],
        "emotional_manipulation": "<yes/no with specific examples>",
        "agenda_detected": "<what agenda is being pushed?>",
        "distraction_tactic": "<is this distracting from real issues?>"
    }},
    "india_relevance": {{
        "score": <0-20>,
        "reasoning": "<CRITICAL assessment - REAL impact on citizens>",
        "claimed_relevance": "<what the report claims is relevant>",
        "actual_relevance": "<what's ACTUALLY relevant to Indian citizens>",
        "impact_areas": ["<real impact areas, not claimed ones>"],
        "relevance_level": "<high/medium/low/none>",
        "how_affects_india": "<REAL impact, not claimed impact>",
        "citizen_concerns": ["<what should citizens be concerned about>"]
    }},
    "overall_score": <0-100>,
    "category": "<DETERMINE BASED ON SCORES - Use specific descriptive category with keywords from article>",
    "category_keywords": ["<list of key terms from article that define its nature>"],
    "category_reasoning": "<explain why this category based on individual scores>",
    "verdict": "<CRITICAL verdict - don't accept at face value, question everything>",
    "india_specific_analysis": {{
        "relevance_to_india": "<CRITICAL - what's the REAL relevance, not claimed>",
        "potential_impact": "<REAL impact on Indian citizens, not claimed>",
        "harm_assessment": "<what harm could this cause? what's being hidden?>",
        "citizen_rights": "<does this serve citizens' right to information?>",
        "recommendation": "<what should citizens do? what should they question?>"
    }},
    "critical_findings": ["<CRITICAL findings - what's wrong, what's missing, what should be questioned>"],
    "fact_check_notes": "<CRITICAL fact-checking - what can't be verified, what's suspicious>",
    "opposition_viewpoint": "<what would an opposition reporter say about this?>",
    "citizen_accountability": {{
        "questions_citizens_should_ask": ["<list of questions Indian citizens should be asking>"],
        "topics_should_have_covered": ["<list of topics the article SHOULD have covered for accountability>"],
        "information_citizens_need": ["<what information do citizens NEED that the article doesn't provide>"],
        "accountability_gaps": ["<what accountability issues should have been addressed>"],
        "transparency_issues": ["<what transparency questions should have been asked>"],
        "real_citizen_impact": "<what's the REAL impact on citizens' lives, rights, interests that wasn't covered>",
        "what_should_have_been_investigated": ["<what should the article have investigated or questioned>"],
        "democratic_accountability": "<how should this have been reported to serve democratic accountability>",
        "citizen_right_to_know": "<what should citizens know that they don't from this article>"
    }},
    "world_class_comparison": {{
        "overall_rating_vs_world_class": <0-100, where 100 = matches world-class standards>,
        "comparison_categories": {{
            "factual_accuracy": {{
                "this_article_score": <0-100>,
                "world_class_standard": 90,
                "gap": <difference>,
                "assessment": "<how this compares to BBC/Reuters standards>"
            }},
            "source_diversity": {{
                "this_article_score": <0-100>,
                "world_class_standard": 85,
                "gap": <difference>,
                "assessment": "<how this compares to world-class source diversity>"
            }},
            "investigative_depth": {{
                "this_article_score": <0-100>,
                "world_class_standard": 88,
                "gap": <difference>,
                "assessment": "<depth comparison with investigative journalism standards>"
            }},
            "balance_and_perspectives": {{
                "this_article_score": <0-100>,
                "world_class_standard": 87,
                "gap": <difference>,
                "assessment": "<how balanced this is vs world-class reporting>"
            }},
            "transparency": {{
                "this_article_score": <0-100>,
                "world_class_standard": 90,
                "gap": <difference>,
                "assessment": "<transparency comparison>"
            }},
            "citizen_focus": {{
                "this_article_score": <0-100>,
                "world_class_standard": 85,
                "gap": <difference>,
                "assessment": "<how well it serves citizens vs world-class standards>"
            }},
            "context_and_background": {{
                "this_article_score": <0-100>,
                "world_class_standard": 88,
                "gap": <difference>,
                "assessment": "<context provided vs world-class standards>"
            }},
            "data_and_evidence": {{
                "this_article_score": <0-100>,
                "world_class_standard": 87,
                "gap": <difference>,
                "assessment": "<data usage vs world-class standards>"
            }},
            "expert_consultation": {{
                "this_article_score": <0-100>,
                "world_class_standard": 85,
                "gap": <difference>,
                "assessment": "<expert input vs world-class standards>"
            }},
            "independence": {{
                "this_article_score": <0-100>,
                "world_class_standard": 90,
                "gap": <difference>,
                "assessment": "<independence from agenda vs world-class standards>"
            }}
        }},
        "world_class_benchmarks": {{
            "bbc_standard": "<how this compares to BBC reporting standards>",
            "reuters_standard": "<how this compares to Reuters standards>",
            "guardian_standard": "<how this compares to The Guardian standards>",
            "nyt_standard": "<how this compares to New York Times standards>",
            "overall_assessment": "<comprehensive comparison with world's best>"
        }},
        "improvement_needed": ["<specific areas where this falls short of world-class standards>"],
        "strengths": ["<areas where this matches or exceeds world-class standards>"]
    }},
    "true_report": {{
        "title": "<how the article SHOULD have been titled - comprehensive and accurate>",
        "lead_paragraph": "<opening paragraph that captures the real story for Indian citizens>",
        "full_report": "<COMPLETE, UNBIASED, COMPREHENSIVE news report (800-1500 words) covering ALL topics from citizen accountability section. This must be a full news article that: 1) Answers ALL questions from questions_citizens_should_ask, 2) Covers ALL topics from topics_should_have_covered, 3) Includes ALL information from information_citizens_need, 4) Addresses ALL accountability gaps, 5) Covers ALL transparency issues, 6) Investigates ALL items from what_should_have_been_investigated, 7) Includes multiple perspectives (government, opposition, experts, citizens), 8) Provides proper context and background, 9) Includes verifiable data and statistics, 10) Focuses on REAL citizen impact, 11) Addresses policy implications, 12) Is balanced, factual, and journalistically sound. Write this as a complete news article that Indian citizens would find informative and accountable.>",
        "sections": {{
            "background_context": "<necessary background and context missing from original>",
            "multiple_perspectives": "<different viewpoints that should have been included>",
            "citizen_impact_analysis": "<detailed analysis of real impact on Indian citizens>",
            "accountability_questions": "<answers to all accountability questions raised>",
            "transparency_issues": "<coverage of transparency issues that should have been addressed>",
            "data_and_evidence": "<verifiable data, statistics, and evidence that should have been included>",
            "expert_opinions": "<what expert opinions and analysis should have been sought>",
            "historical_context": "<historical context and precedents relevant to Indian citizens>",
            "policy_implications": "<policy implications and government accountability aspects>",
            "citizen_rights_impact": "<how this affects citizens' rights, interests, and democratic participation>"
        }},
        "sources_and_references": {{
            "primary_sources": ["<what primary sources should have been consulted>"],
            "expert_sources": ["<what experts should have been quoted>"],
            "official_sources": ["<what official/government sources should have been accessed>"],
            "data_sources": ["<what data sources and statistics should have been referenced>"],
            "independent_sources": ["<what independent verification sources should have been used>"],
            "opposition_perspectives": ["<what opposition or alternative perspectives should have been included>"]
        }},
        "reporting_standards": {{
            "what_was_missing": "<summary of what was missing in original report>",
            "how_to_improve": "<how the reporting should have been improved>",
            "journalistic_standards": "<what journalistic standards should have been followed>",
            "citizen_focus": "<how the report should have focused on citizen interests>"
        }}
    }}
}}

BE CRITICAL. QUESTION EVERYTHING. DON'T ACCEPT AT FACE VALUE. 
Act like an opposition reporter demanding answers. 
"Roast" the report with questions, then judge it based on what answers it provides.
Focus on what Indian citizens NEED to know vs. what's being reported.
Be harsh but fair - if it's good reporting, say so. If it's propaganda, call it out."""
        
        return prompt
    
    def analyze_news(self, url: str, find_related: bool = True) -> Dict[str, Any]:
        """Main method to analyze a news article"""
        print(f"\n🔍 Fetching article from: {url}")
        
        # Fetch article content
        article_data = self.fetch_article_content(url)
        if not article_data.get("success"):
            return {
                "success": False,
                "error": f"Failed to fetch article: {article_data.get('error')}",
                "url": url
            }
        
        print(f"✅ Article fetched: {article_data.get('title', 'N/A')}")
        print(f"📄 Content length: {len(article_data.get('content', ''))} characters")
        
        # Find related articles from same website (with timeout protection)
        related_articles_analysis = None
        if find_related:
            print("🔗 Searching for related articles on the same website...")
            try:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Related articles search timed out")
                
                # Set 30 second timeout for related articles search
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                try:
                    related_articles = self.find_related_articles(
                        url, 
                        article_data.get('title', ''), 
                        article_data.get('content', ''),
                        max_articles=5
                    )
                    signal.alarm(0)  # Cancel timeout
                    
                    if related_articles:
                        print(f"   ✅ Found {len(related_articles)} related articles")
                        related_articles_analysis = self.analyze_related_articles(article_data, related_articles)
                    else:
                        print("   ⚠️  No related articles found")
                except TimeoutError:
                    signal.alarm(0)
                    print("   ⚠️  Related articles search timed out (skipping)")
                except Exception as e:
                    signal.alarm(0)
                    print(f"   ⚠️  Error finding related articles: {str(e)}")
            except Exception as e:
                print(f"   ⚠️  Error in related articles search: {str(e)}")
        
        # Load rules
        print("📋 Loading analysis rules...")
        rules = self.load_rules()
        
        # Create analysis prompt
        print("🤖 Creating analysis prompt...")
        prompt = self.create_analysis_prompt(article_data, rules)
        
        # Call OpenAI API
        print("🧠 Analyzing with OpenAI...")
        print("   ⏳ This may take 30-90 seconds, please wait...")
        try:
            # Use the model that worked during API key test
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is to QUESTION EVERYTHING, identify what's MISSING, challenge claims, and demand answers that Indian citizens deserve. Don't accept reports at face value - be skeptical, ask hard questions, and judge based on what answers the report provides. Act like an adversarial journalist who wants the truth, not just what's being told."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,  # Slightly higher for more creative comprehensive reporting
                max_tokens=4000  # Increased to accommodate comprehensive True Report
            )
            
            analysis_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    analysis_text = analysis_text[json_start:json_end].strip()
                elif "```" in analysis_text:
                    json_start = analysis_text.find("```") + 3
                    json_end = analysis_text.find("```", json_start)
                    analysis_text = analysis_text[json_start:json_end].strip()
                
                analysis_json = json.loads(analysis_text)
                
                # Refine category based on individual scores
                analysis_json = self.refine_category_based_on_scores(analysis_json, article_data)
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return the text response
                analysis_json = {
                    "raw_response": analysis_text,
                    "parse_error": "Could not parse JSON response"
                }
            
            result = {
                "success": True,
                "url": url,
                "article": article_data,
                "analysis": analysis_json,
                "raw_response": analysis_text
            }
            
            # Add related articles analysis if available
            if related_articles_analysis:
                result["related_articles"] = related_articles_analysis
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}",
                "url": url,
                "article": article_data
            }
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format the analysis result for display"""
        if not result.get("success"):
            return f"❌ Error: {result.get('error')}\n"
        
        analysis = result.get("analysis", {})
        article = result.get("article", {})
        
        output = []
        output.append("=" * 80)
        output.append("📰 NEWS ANALYSIS REPORT")
        output.append("=" * 80)
        output.append(f"\n🔗 URL: {result.get('url')}")
        output.append(f"📌 Title: {article.get('title', 'N/A')}")
        output.append("\n" + "-" * 80)
        
        # Overall verdict
        if isinstance(analysis, dict):
            category = analysis.get("category", "UNKNOWN")
            overall_score = analysis.get("overall_score", "N/A")
            
            output.append(f"\n🎯 OVERALL VERDICT: {category}")
            output.append(f"📊 Overall Score: {overall_score}/100")
            
            # Category reasoning and keywords
            if "category_reasoning" in analysis and analysis.get("category_reasoning"):
                output.append(f"   📝 Category Reasoning: {analysis.get('category_reasoning')}")
            if "category_keywords" in analysis and analysis.get("category_keywords"):
                output.append(f"   🔑 Key Terms: {', '.join(analysis['category_keywords'][:5])}")
            
            # Critical Questions Section
            if "critical_questions" in analysis:
                output.append("\n" + "-" * 80)
                output.append("❓ CRITICAL QUESTIONS - What Should Citizens Ask?")
                output.append("-" * 80)
                cq = analysis["critical_questions"]
                
                if "questions_raised" in cq and cq["questions_raised"]:
                    output.append("\n🔍 Questions That Should Be Asked:")
                    for i, q in enumerate(cq["questions_raised"], 1):
                        output.append(f"   {i}. {q}")
                
                if "questions_unanswered" in cq and cq["questions_unanswered"]:
                    output.append("\n❌ Questions NOT Answered by This Report:")
                    for i, q in enumerate(cq["questions_unanswered"], 1):
                        output.append(f"   {i}. {q}")
                
                if "missing_perspectives" in cq and cq["missing_perspectives"]:
                    output.append("\n👥 Missing Perspectives:")
                    for i, p in enumerate(cq["missing_perspectives"], 1):
                        output.append(f"   {i}. {p}")
                
                if "hidden_agenda" in cq and cq.get("hidden_agenda"):
                    output.append(f"\n🎭 Possible Hidden Agenda: {cq.get('hidden_agenda')}")
            
            # Opposition Viewpoint
            if "opposition_viewpoint" in analysis and analysis.get("opposition_viewpoint"):
                output.append("\n" + "-" * 80)
                output.append("🗣️  OPPOSITION VIEWPOINT:")
                output.append("-" * 80)
                output.append(f"\n{analysis.get('opposition_viewpoint')}")
            
            # Beneficiary Analysis Section
            if "beneficiary_analysis" in analysis:
                output.append("\n" + "=" * 80)
                output.append("💰 BENEFICIARY & HIDDEN AGENDA ANALYSIS")
                output.append("=" * 80)
                output.append("Who Benefits? What's Being Hidden?")
                output.append("=" * 80)
                
                ba = analysis["beneficiary_analysis"]
                
                if "people_involved" in ba and ba.get("people_involved"):
                    output.append("\n👥 PEOPLE/ENTITIES INVOLVED:")
                    for i, person in enumerate(ba["people_involved"], 1):
                        output.append(f"   {i}. {person}")
                
                if "direct_beneficiaries" in ba and ba.get("direct_beneficiaries"):
                    output.append("\n✅ DIRECT BENEFICIARIES (Who Directly Gains):")
                    for i, beneficiary in enumerate(ba["direct_beneficiaries"], 1):
                        output.append(f"   {i}. {beneficiary}")
                
                if "indirect_beneficiaries" in ba and ba.get("indirect_beneficiaries"):
                    output.append("\n🔗 INDIRECT BENEFICIARIES (Who Gains Indirectly):")
                    for i, beneficiary in enumerate(ba["indirect_beneficiaries"], 1):
                        output.append(f"   {i}. {beneficiary}")
                
                if "political_beneficiaries" in ba and ba.get("political_beneficiaries"):
                    output.append("\n🏛️  POLITICAL BENEFICIARIES:")
                    for i, beneficiary in enumerate(ba["political_beneficiaries"], 1):
                        output.append(f"   {i}. {beneficiary}")
                
                if "economic_beneficiaries" in ba and ba.get("economic_beneficiaries"):
                    output.append("\n💵 ECONOMIC BENEFICIARIES:")
                    for i, beneficiary in enumerate(ba["economic_beneficiaries"], 1):
                        output.append(f"   {i}. {beneficiary}")
                
                if "connections_and_relationships" in ba:
                    connections = ba["connections_and_relationships"]
                    output.append("\n🔗 CONNECTIONS & RELATIONSHIPS:")
                    
                    if "media_connections" in connections and connections.get("media_connections"):
                        output.append("\n   📺 Media Connections:")
                        for conn in connections["media_connections"][:5]:
                            output.append(f"      • {conn}")
                    
                    if "business_relationships" in connections and connections.get("business_relationships"):
                        output.append("\n   💼 Business Relationships:")
                        for conn in connections["business_relationships"][:5]:
                            output.append(f"      • {conn}")
                    
                    if "political_affiliations" in connections and connections.get("political_affiliations"):
                        output.append("\n   🏛️  Political Affiliations:")
                        for conn in connections["political_affiliations"][:5]:
                            output.append(f"      • {conn}")
                    
                    if "undisclosed_relationships" in connections and connections.get("undisclosed_relationships"):
                        output.append("\n   ⚠️  UNDISCLOSED RELATIONSHIPS:")
                        for conn in connections["undisclosed_relationships"][:5]:
                            output.append(f"      • {conn}")
                
                if "conflict_of_interest" in ba and ba.get("conflict_of_interest"):
                    output.append("\n⚠️  CONFLICTS OF INTEREST:")
                    for i, conflict in enumerate(ba["conflict_of_interest"], 1):
                        output.append(f"   {i}. {conflict}")
                
                if "real_news_hidden" in ba and ba.get("real_news_hidden"):
                    output.append("\n🔍 REAL NEWS BEING HIDDEN:")
                    output.append(f"   {ba.get('real_news_hidden')}")
                
                if "agenda_masking" in ba and ba.get("agenda_masking"):
                    output.append("\n🎭 AGENDA MASKING (What Bigger Story is Hidden):")
                    output.append(f"   {ba.get('agenda_masking')}")
                
                if "timing_analysis" in ba and ba.get("timing_analysis"):
                    output.append("\n⏰ TIMING ANALYSIS (Why Now?):")
                    output.append(f"   {ba.get('timing_analysis')}")
                
                if "distraction_purpose" in ba and ba.get("distraction_purpose"):
                    output.append("\n🎪 DISTRACTION PURPOSE:")
                    output.append(f"   {ba.get('distraction_purpose')}")
                
                if "who_loses" in ba and ba.get("who_loses"):
                    output.append("\n❌ WHO STANDS TO LOSE (If Real Story Comes Out):")
                    for i, entity in enumerate(ba["who_loses"], 1):
                        output.append(f"   {i}. {entity}")
            
            # Detailed scores
            output.append("\n" + "-" * 80)
            output.append("📈 DETAILED SCORING:")
            output.append("-" * 80)
            
            if "factual_accuracy" in analysis:
                fa = analysis["factual_accuracy"]
                output.append(f"\n✅ Factual Accuracy: {fa.get('score', 'N/A')}/30")
                output.append(f"   {fa.get('reasoning', 'N/A')}")
                if "missing_evidence" in fa and fa.get("missing_evidence"):
                    output.append(f"   ⚠️  Missing Evidence: {', '.join(fa['missing_evidence'][:3])}")
            
            if "source_credibility" in analysis:
                sc = analysis["source_credibility"]
                output.append(f"\n📚 Source Credibility: {sc.get('score', 'N/A')}/20")
                output.append(f"   {sc.get('reasoning', 'N/A')}")
                if "sources_missing" in sc and sc.get("sources_missing"):
                    output.append(f"   ⚠️  Missing Sources: {', '.join(sc['sources_missing'][:3])}")
                if "one_sided" in sc and sc.get("one_sided", "").lower() in ["yes", "true"]:
                    output.append(f"   ⚠️  One-Sided Reporting: {sc.get('one_sided')}")
            
            if "bias_level" in analysis:
                bl = analysis["bias_level"]
                output.append(f"\n⚖️  Bias Level: {bl.get('score', 'N/A')}/15")
                output.append(f"   {bl.get('reasoning', 'N/A')}")
            
            if "propaganda_indicators" in analysis:
                pi = analysis["propaganda_indicators"]
                output.append(f"\n🚨 Propaganda Indicators: {pi.get('score', 'N/A')}/15")
                output.append(f"   {pi.get('reasoning', 'N/A')}")
            
            if "india_relevance" in analysis:
                ir = analysis["india_relevance"]
                output.append(f"\n🇮🇳 India Relevance: {ir.get('score', 'N/A')}/20")
                output.append(f"   {ir.get('reasoning', 'N/A')}")
                if "claimed_relevance" in ir and ir.get("claimed_relevance"):
                    output.append(f"   📢 Claimed: {ir.get('claimed_relevance')}")
                if "actual_relevance" in ir and ir.get("actual_relevance"):
                    output.append(f"   ✅ Actual: {ir.get('actual_relevance')}")
                if "citizen_concerns" in ir and ir.get("citizen_concerns"):
                    output.append(f"   👥 Citizen Concerns: {', '.join(ir['citizen_concerns'][:3])}")
            
            # India-specific analysis
            if "india_specific_analysis" in analysis:
                output.append("\n" + "-" * 80)
                output.append("🇮🇳 INDIA-SPECIFIC ANALYSIS:")
                output.append("-" * 80)
                isa = analysis["india_specific_analysis"]
                output.append(f"\n📌 Relevance: {isa.get('relevance_to_india', 'N/A')}")
                output.append(f"\n💡 Impact: {isa.get('potential_impact', 'N/A')}")
                output.append(f"\n⚠️  Harm Assessment: {isa.get('harm_assessment', 'N/A')}")
                if "citizen_rights" in isa and isa.get("citizen_rights"):
                    output.append(f"\n⚖️  Citizen Rights: {isa.get('citizen_rights')}")
                output.append(f"\n💬 Recommendation: {isa.get('recommendation', 'N/A')}")
            
            # Verdict
            if "verdict" in analysis:
                output.append("\n" + "-" * 80)
                output.append("📋 COMPREHENSIVE VERDICT:")
                output.append("-" * 80)
                output.append(f"\n{analysis.get('verdict', 'N/A')}")
            
            # Citizen Accountability Section - Most Important
            if "citizen_accountability" in analysis:
                output.append("\n" + "=" * 80)
                output.append("👥 CITIZEN ACCOUNTABILITY - What Should Have Been Reported")
                output.append("=" * 80)
                ca = analysis["citizen_accountability"]
                
                if "questions_citizens_should_ask" in ca and ca["questions_citizens_should_ask"]:
                    output.append("\n❓ Questions Indian Citizens Should Be Asking:")
                    for i, q in enumerate(ca["questions_citizens_should_ask"], 1):
                        output.append(f"   {i}. {q}")
                
                if "topics_should_have_covered" in ca and ca["topics_should_have_covered"]:
                    output.append("\n📋 Topics Article SHOULD Have Covered (For Accountability):")
                    for i, topic in enumerate(ca["topics_should_have_covered"], 1):
                        output.append(f"   {i}. {topic}")
                
                if "information_citizens_need" in ca and ca["information_citizens_need"]:
                    output.append("\n📰 Information Citizens NEED (But Article Doesn't Provide):")
                    for i, info in enumerate(ca["information_citizens_need"], 1):
                        output.append(f"   {i}. {info}")
                
                if "accountability_gaps" in ca and ca["accountability_gaps"]:
                    output.append("\n⚖️  Accountability Gaps (What Should Have Been Addressed):")
                    for i, gap in enumerate(ca["accountability_gaps"], 1):
                        output.append(f"   {i}. {gap}")
                
                if "transparency_issues" in ca and ca["transparency_issues"]:
                    output.append("\n🔍 Transparency Issues (Questions That Should Have Been Asked):")
                    for i, issue in enumerate(ca["transparency_issues"], 1):
                        output.append(f"   {i}. {issue}")
                
                if "what_should_have_been_investigated" in ca and ca["what_should_have_been_investigated"]:
                    output.append("\n🔎 What Should Have Been Investigated:")
                    for i, inv in enumerate(ca["what_should_have_been_investigated"], 1):
                        output.append(f"   {i}. {inv}")
                
                if "real_citizen_impact" in ca and ca.get("real_citizen_impact"):
                    output.append(f"\n💡 Real Impact on Citizens (Not Covered):")
                    output.append(f"   {ca.get('real_citizen_impact')}")
                
                if "democratic_accountability" in ca and ca.get("democratic_accountability"):
                    output.append(f"\n🗳️  Democratic Accountability (How It Should Have Been Reported):")
                    output.append(f"   {ca.get('democratic_accountability')}")
                
                if "citizen_right_to_know" in ca and ca.get("citizen_right_to_know"):
                    output.append(f"\n📜 Citizen's Right to Know (What's Missing):")
                    output.append(f"   {ca.get('citizen_right_to_know')}")
            
            # World-Class Comparison Section
            if "world_class_comparison" in analysis:
                output.append("\n" + "=" * 80)
                output.append("🌍 WORLD-CLASS REPORTING COMPARISON")
                output.append("=" * 80)
                
                wcc = analysis["world_class_comparison"]
                overall_rating = wcc.get("overall_rating_vs_world_class", 0)
                output.append(f"\n📊 Overall Rating vs World-Class Standards: {overall_rating}/100")
                
                if "comparison_categories" in wcc:
                    output.append("\n📈 Category-by-Category Comparison:")
                    output.append("-" * 80)
                    
                    categories = wcc["comparison_categories"]
                    for cat_name, cat_data in categories.items():
                        if isinstance(cat_data, dict):
                            cat_display = cat_name.replace("_", " ").title()
                            article_score = cat_data.get("this_article_score", 0)
                            world_std = cat_data.get("world_class_standard", 85)
                            gap = cat_data.get("gap", 0)
                            
                            output.append(f"\n   {cat_display}:")
                            output.append(f"      This Article: {article_score}/100")
                            output.append(f"      World Standard: {world_std}/100")
                            output.append(f"      Gap: {gap:+.0f} points")
                            if cat_data.get("assessment"):
                                output.append(f"      Assessment: {cat_data.get('assessment')}")
                
                if "world_class_benchmarks" in wcc:
                    benchmarks = wcc["world_class_benchmarks"]
                    output.append("\n🏆 Comparison with World's Best:")
                    output.append("-" * 80)
                    
                    if "bbc_standard" in benchmarks:
                        output.append(f"\n   BBC: {benchmarks['bbc_standard']}")
                    if "reuters_standard" in benchmarks:
                        output.append(f"\n   Reuters: {benchmarks['reuters_standard']}")
                    if "guardian_standard" in benchmarks:
                        output.append(f"\n   The Guardian: {benchmarks['guardian_standard']}")
                    if "nyt_standard" in benchmarks:
                        output.append(f"\n   New York Times: {benchmarks['nyt_standard']}")
                    if "overall_assessment" in benchmarks:
                        output.append(f"\n   Overall: {benchmarks['overall_assessment']}")
                
                if "strengths" in wcc and wcc.get("strengths"):
                    output.append("\n✅ Strengths (Matches World-Class):")
                    for strength in wcc["strengths"]:
                        output.append(f"   • {strength}")
                
                if "improvement_needed" in wcc and wcc.get("improvement_needed"):
                    output.append("\n⚠️  Areas Needing Improvement:")
                    for improvement in wcc["improvement_needed"]:
                        output.append(f"   • {improvement}")
            
            # True Report Section - How It Should Have Been Reported
            if "true_report" in analysis:
                output.append("\n" + "=" * 80)
                output.append("📰 TRUE REPORT - How This Should Have Been Reported")
                output.append("=" * 80)
                output.append("A complete, unbiased report covering all topics for Indian citizens")
                output.append("=" * 80)
                
                tr = analysis["true_report"]
                
                if "title" in tr and tr.get("title"):
                    output.append(f"\n📌 PROPER TITLE:")
                    output.append(f"   {tr.get('title')}")
                
                if "lead_paragraph" in tr and tr.get("lead_paragraph"):
                    output.append(f"\n📝 LEAD PARAGRAPH:")
                    output.append(f"   {tr.get('lead_paragraph')}")
                
                if "full_report" in tr and tr.get("full_report"):
                    output.append(f"\n📄 COMPLETE REPORT:")
                    output.append("-" * 80)
                    # Split into paragraphs for readability
                    report = tr.get("full_report")
                    paragraphs = [p.strip() for p in report.split('\n\n') if p.strip()]
                    for para in paragraphs:
                        output.append(f"\n{para}")
                    output.append("-" * 80)
                
                if "sections" in tr:
                    sections = tr["sections"]
                    output.append(f"\n📋 REPORT SECTIONS:")
                    
                    section_order = [
                        ("background_context", "Background & Context"),
                        ("multiple_perspectives", "Multiple Perspectives"),
                        ("citizen_impact_analysis", "Citizen Impact Analysis"),
                        ("accountability_questions", "Accountability Questions Answered"),
                        ("transparency_issues", "Transparency Issues"),
                        ("data_and_evidence", "Data & Evidence"),
                        ("expert_opinions", "Expert Opinions"),
                        ("historical_context", "Historical Context"),
                        ("policy_implications", "Policy Implications"),
                        ("citizen_rights_impact", "Citizen Rights Impact")
                    ]
                    
                    for key, label in section_order:
                        if key in sections and sections.get(key):
                            output.append(f"\n   🔹 {label}:")
                            content = sections[key]
                            if isinstance(content, list):
                                for item in content:
                                    output.append(f"      • {item}")
                            else:
                                # Split long content into lines
                                lines = content.split('. ')
                                for line in lines[:5]:  # Limit to first 5 points
                                    if line.strip():
                                        output.append(f"      • {line.strip()}.")
            
                if "sources_and_references" in tr:
                    sources = tr["sources_and_references"]
                    output.append(f"\n📚 SOURCES & REFERENCES (What Should Have Been Used):")
                    
                    if "primary_sources" in sources and sources.get("primary_sources"):
                        output.append(f"\n   📄 Primary Sources:")
                        for src in sources["primary_sources"][:5]:
                            output.append(f"      • {src}")
                    
                    if "expert_sources" in sources and sources.get("expert_sources"):
                        output.append(f"\n   👨‍🔬 Expert Sources:")
                        for src in sources["expert_sources"][:5]:
                            output.append(f"      • {src}")
                    
                    if "official_sources" in sources and sources.get("official_sources"):
                        output.append(f"\n   🏛️  Official Sources:")
                        for src in sources["official_sources"][:5]:
                            output.append(f"      • {src}")
                    
                    if "data_sources" in sources and sources.get("data_sources"):
                        output.append(f"\n   📊 Data Sources:")
                        for src in sources["data_sources"][:5]:
                            output.append(f"      • {src}")
                    
                    if "independent_sources" in sources and sources.get("independent_sources"):
                        output.append(f"\n   🔍 Independent Sources:")
                        for src in sources["independent_sources"][:5]:
                            output.append(f"      • {src}")
                    
                    if "opposition_perspectives" in sources and sources.get("opposition_perspectives"):
                        output.append(f"\n   ⚖️  Opposition/Alternative Perspectives:")
                        for src in sources["opposition_perspectives"][:5]:
                            output.append(f"      • {src}")
                
                if "reporting_standards" in tr:
                    standards = tr["reporting_standards"]
                    output.append(f"\n📋 REPORTING STANDARDS:")
                    
                    if "what_was_missing" in standards and standards.get("what_was_missing"):
                        output.append(f"\n   ❌ What Was Missing in Original:")
                        output.append(f"      {standards.get('what_was_missing')}")
                    
                    if "how_to_improve" in standards and standards.get("how_to_improve"):
                        output.append(f"\n   ✅ How Reporting Should Be Improved:")
                        output.append(f"      {standards.get('how_to_improve')}")
                    
                    if "journalistic_standards" in standards and standards.get("journalistic_standards"):
                        output.append(f"\n   📰 Journalistic Standards:")
                        output.append(f"      {standards.get('journalistic_standards')}")
                    
                    if "citizen_focus" in standards and standards.get("citizen_focus"):
                        output.append(f"\n   👥 Citizen-Focused Reporting:")
                        output.append(f"      {standards.get('citizen_focus')}")
            
            # Related Articles Section
            if "related_articles" in result:
                output.append("\n" + "=" * 80)
                output.append("🔗 RELATED ARTICLES & THEIR RELEVANCE")
                output.append("=" * 80)
                
                ra = result["related_articles"]
                if ra.get("related_articles_found"):
                    output.append(f"\n📰 Found {ra.get('total_found', 0)} related articles on the same website")
                    output.append("\n" + "-" * 80)
                    
                    for i, article in enumerate(ra.get("articles", []), 1):
                        output.append(f"\n{i}. {article.get('title', 'No title')}")
                        output.append(f"   🔗 URL: {article.get('url', 'N/A')}")
                        output.append(f"   📊 Relevance Score: {article.get('relevance_score', 0)}")
                        
                        if article.get('summary'):
                            output.append(f"   📝 Summary: {article.get('summary', '')[:150]}...")
                        
                        comparison = article.get("comparison", {})
                        if comparison:
                            if comparison.get("common_topics"):
                                output.append(f"   🔄 Common Topics: {', '.join(comparison['common_topics'][:5])}")
                            
                            if comparison.get("topics_in_related_not_in_current"):
                                output.append(f"   ➕ Topics in Related (Missing in Current): {', '.join(comparison['topics_in_related_not_in_current'][:5])}")
                            
                            if comparison.get("information_in_related_not_in_current"):
                                output.append(f"   ⚠️  Information in Related Article (Not in Current):")
                                for info in comparison["information_in_related_not_in_current"]:
                                    output.append(f"      • {info[:200]}...")
                        
                        output.append("")  # Empty line between articles
                else:
                    output.append(f"\n{ra.get('message', 'No related articles found')}")
            
            # Critical findings (preferred) or key findings
            if "critical_findings" in analysis:
                output.append("\n" + "-" * 80)
                output.append("🔍 CRITICAL FINDINGS - What's Wrong, What's Missing:")
                output.append("-" * 80)
                for i, finding in enumerate(analysis["critical_findings"], 1):
                    output.append(f"\n{i}. {finding}")
            elif "key_findings" in analysis:
                output.append("\n" + "-" * 80)
                output.append("🔍 KEY FINDINGS:")
                output.append("-" * 80)
                for i, finding in enumerate(analysis["key_findings"], 1):
                    output.append(f"\n{i}. {finding}")
        
        else:
            output.append("\n⚠️  Could not parse analysis. Raw response:")
            output.append(str(analysis))
        
        output.append("\n" + "=" * 80)
        
        return "\n".join(output)


def main():
    """Main function to test and run the analyzer"""
    print("🚀 Initializing News Analyzer...")
    
    try:
        analyzer = NewsAnalyzer()
        
        # Test API key
        print("\n🔑 Testing OpenAI API key...")
        if analyzer.test_api_key():
            print("✅ API key is working!")
        else:
            print("❌ API key test failed!")
            return
        
        # Interactive mode
        print("\n" + "=" * 80)
        print("📰 NEWS ANALYZER - Fact-Checking & Propaganda Detection")
        print("=" * 80)
        print("\nEnter a news URL to analyze (or 'quit' to exit):")
        
        while True:
            url = input("\n🔗 URL: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not url:
                print("⚠️  Please enter a valid URL")
                continue
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Analyze the news
            result = analyzer.analyze_news(url)
            
            # Display results
            print("\n" + analyzer.format_output(result))
            
            # Ask if user wants to continue
            continue_analysis = input("\n\nAnalyze another article? (y/n): ").strip().lower()
            if continue_analysis != 'y':
                print("\n👋 Goodbye!")
                break
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


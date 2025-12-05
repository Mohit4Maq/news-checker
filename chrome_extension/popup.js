// Default Streamlit app URL (user can change this)
const DEFAULT_STREAMLIT_URL = 'https://newsfactchecker.streamlit.app';

// Function to extract content directly (runs in page context)
function extractContentDirectly() {
    const result = {
        url: window.location.href,
        title: '',
        content: ''
    };
    
    // Extract title - try multiple methods
    const titleSelectors = [
        'h1',
        '[property="og:title"]',
        '[name="twitter:title"]',
        'meta[property="og:title"]',
        'title'
    ];
    for (const selector of titleSelectors) {
        try {
            const element = document.querySelector(selector);
            if (element) {
                result.title = element.textContent || element.getAttribute('content') || element.innerText || '';
                if (result.title && result.title.trim()) {
                    result.title = result.title.trim();
                    break;
                }
            }
        } catch(e) {}
    }
    
    // Try to extract main article content - more comprehensive selectors
    const contentSelectors = [
        'article',
        '[role="article"]',
        '.article-content',
        '.article-body',
        '.post-content',
        '.story-body',
        '.content-body',
        '.entry-content',
        '.article-text',
        '.article-main',
        '.story-content',
        '.news-content',
        '.news-body',
        'main article',
        '.article',
        '.story',
        '.news-article',
        '[class*="article"]',
        '[class*="story"]',
        '[class*="content"]',
        '[id*="article"]',
        '[id*="content"]',
        '[id*="story"]'
    ];
    
    let articleElement = null;
    let bestContent = '';
    let bestLength = 0;
    
    // Try all selectors and keep the one with most content
    for (const selector of contentSelectors) {
        try {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const text = el.innerText || el.textContent || '';
                if (text.length > bestLength && text.length > 100) {
                    bestContent = text;
                    bestLength = text.length;
                    articleElement = el;
                }
            }
        } catch(e) {}
    }
    
    if (articleElement && bestContent) {
        result.content = bestContent;
    } else {
        // Fallback: get body text but filter out navigation more aggressively
        const body = document.body;
        if (body) {
            const clone = body.cloneNode(true);
            
            // Remove common non-content elements
            const removeSelectors = [
                'nav', 'header', 'footer', 'aside', 'script', 'style', 'iframe',
                '.nav', '.navigation', '.menu', '.sidebar', '.ad', '.advertisement',
                '.social', '.share', '.comment', '.related', '.recommended',
                '.trending', '.newsletter', '.subscribe', '.cookie', '.consent',
                '[class*="nav"]', '[class*="menu"]', '[class*="ad"]',
                '[class*="social"]', '[class*="share"]', '[id*="nav"]',
                '[id*="menu"]', '[id*="ad"]', '[role="navigation"]',
                '[role="banner"]', '[role="complementary"]'
            ];
            
            removeSelectors.forEach(sel => {
                try {
                    clone.querySelectorAll(sel).forEach(el => el.remove());
                } catch(e) {}
            });
            
            // Get all paragraphs
            const paragraphs = clone.querySelectorAll('p');
            if (paragraphs.length > 0) {
                const paraTexts = [];
                paragraphs.forEach(p => {
                    const text = (p.innerText || p.textContent || '').trim();
                    // Only keep substantial paragraphs (not navigation/menu items)
                    if (text.length > 20 && !text.match(/^(cookie|subscribe|follow|menu|home|about|contact)/i)) {
                        paraTexts.push(text);
                    }
                });
                result.content = paraTexts.join('\n\n');
            } else {
                result.content = clone.innerText || clone.textContent || '';
            }
        }
    }
    
    // Clean up content - more aggressive
    if (result.content) {
        result.content = result.content
            .replace(/\n{3,}/g, '\n\n')  // Max 2 newlines
            .replace(/[ \t]{2,}/g, ' ')   // Multiple spaces to single
            .replace(/^\s+|\s+$/gm, '')   // Trim each line
            .trim();
        
        // Remove very short lines that are likely navigation
        const lines = result.content.split('\n');
        const filteredLines = lines.filter(line => {
            const trimmed = line.trim();
            return trimmed.length > 10 && !trimmed.match(/^(cookie|subscribe|follow|menu|home|about|contact|skip|jump)/i);
        });
        result.content = filteredLines.join('\n');
    }
    
    return result;
}

// Get current tab URL
document.addEventListener('DOMContentLoaded', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentUrl = tab.url;
    
    // Display current URL
    const urlDisplay = document.getElementById('currentUrl');
    if (urlDisplay) {
        urlDisplay.textContent = currentUrl || 'No URL found';
    }
    
    // Load saved Streamlit URL
    chrome.storage.sync.get(['streamlitUrl'], (result) => {
        const streamlitUrl = result.streamlitUrl || DEFAULT_STREAMLIT_URL;
        const urlInput = document.getElementById('streamlitUrl');
        urlInput.value = streamlitUrl;
        
        // If no custom URL is saved, save the default one
        if (!result.streamlitUrl) {
            chrome.storage.sync.set({ streamlitUrl: DEFAULT_STREAMLIT_URL });
        }
    });
    
    // Save Streamlit URL when changed (also on blur for better UX)
    const streamlitUrlInput = document.getElementById('streamlitUrl');
    streamlitUrlInput.addEventListener('change', (e) => {
        const url = e.target.value.trim();
        if (url) {
            chrome.storage.sync.set({ streamlitUrl: url });
            showStatus('success', 'URL saved!');
        }
    });
    streamlitUrlInput.addEventListener('blur', (e) => {
        const url = e.target.value.trim();
        if (url) {
            chrome.storage.sync.set({ streamlitUrl: url });
        }
    });
    
    // Analyze button - NEW: Extract content from page and send to Streamlit
    document.getElementById('analyzeBtn').addEventListener('click', async () => {
        const streamlitUrl = document.getElementById('streamlitUrl').value || DEFAULT_STREAMLIT_URL;
        const statusDiv = document.getElementById('status');
        
        if (!currentUrl || !currentUrl.startsWith('http')) {
            showStatus('error', 'Invalid URL. Please navigate to a news article.');
            return;
        }
        
        if (!streamlitUrl || streamlitUrl.trim() === '') {
            showStatus('error', 'Please set your Streamlit app URL in the settings above.');
            return;
        }
        
        try {
            showStatus('info', 'Extracting article content...');
            
            // Get active tab to send message to content script
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab || !tab.id) {
                throw new Error('Could not get active tab');
            }
            
            // Track if extraction succeeded
            let extractionSuccess = false;
            
            // Set a timeout to ensure we always redirect (max 3 seconds)
            const redirectTimeout = setTimeout(() => {
                if (!extractionSuccess) {
                    console.log('Extraction timeout - using URL method');
                    const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                    showStatus('info', 'Opening News Checker...');
                    chrome.tabs.create({ url: analyzeUrl });
                    setTimeout(() => window.close(), 500);
                }
            }, 3000);
            
            // Try direct extraction first (more reliable) - no need to inject content.js
            try {
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: extractContentDirectly
                });
                
                if (results && results[0] && results[0].result) {
                    const articleData = results[0].result;
                    
                    // Safely get content length
                    let contentLength = 0;
                    try {
                        if (articleData && articleData.content && typeof articleData.content === 'string') {
                            contentLength = articleData.content.length;
                        }
                    } catch (e) {
                        console.error('Error getting content length:', e);
                    }
                    
                    console.log('Extraction result:', {
                        hasContent: !!(articleData && articleData.content),
                        contentLength: contentLength,
                        title: articleData ? articleData.title : 'No title'
                    });
                    
                    // Lower threshold - accept even shorter content (30 chars minimum)
                    if (articleData && articleData.content && typeof articleData.content === 'string' && contentLength > 30) {
                        const contentData = {
                            url: articleData.url,
                            title: articleData.title,
                            content: articleData.content
                        };
                        
                        // Use Unicode-safe base64 encoding
                        const jsonString = JSON.stringify(contentData);
                        const encoded = btoa(unescape(encodeURIComponent(jsonString)));
                        const fullUrl = `${streamlitUrl}?content=${encodeURIComponent(encoded)}`;
                        
                        // Check URL length (most servers limit to ~2000-8000 chars)
                        // Streamlit Cloud typically allows ~2000 chars for query params
                        if (fullUrl.length > 2000) {
                            // URL too long - truncate content or use URL method
                            console.log('URL too long (' + fullUrl.length + ' chars), truncating content...');
                            
                            // Try with truncated content (keep first 80% to leave room for encoding overhead)
                            const maxContentLength = Math.floor(articleData.content.length * 0.8);
                            contentData.content = articleData.content.substring(0, maxContentLength) + '\n\n[Content truncated due to URL length limit. Full content available on source page.]';
                            
                            const truncatedJson = JSON.stringify(contentData);
                            const truncatedEncoded = btoa(unescape(encodeURIComponent(truncatedJson)));
                            const truncatedUrl = `${streamlitUrl}?content=${encodeURIComponent(truncatedEncoded)}`;
                            
                            if (truncatedUrl.length <= 2000) {
                                clearTimeout(redirectTimeout);
                                showStatus('warning', 'Content truncated due to length. Opening News Checker...');
                                chrome.tabs.create({ url: truncatedUrl });
                                setTimeout(() => window.close(), 500);
                                extractionSuccess = true;
                                return;
                            } else {
                                // Still too long, fall back to URL method
                                clearTimeout(redirectTimeout);
                                console.log('Even truncated URL too long, using URL method');
                                showStatus('info', 'Content too long, using URL method...');
                                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                                chrome.tabs.create({ url: analyzeUrl });
                                setTimeout(() => window.close(), 500);
                                extractionSuccess = true;
                                return;
                            }
                        }
                        
                        clearTimeout(redirectTimeout);
                        showStatus('success', 'Content extracted! Opening News Checker...');
                        chrome.tabs.create({ url: fullUrl });
                        setTimeout(() => window.close(), 500);
                        extractionSuccess = true;
                        return;
                    } else {
                        console.log('Extraction returned insufficient content:', {
                            hasContent: !!(articleData && articleData.content),
                            length: contentLength,
                            type: articleData && articleData.content ? typeof articleData.content : 'undefined'
                        });
                    }
                } else {
                    console.log('Extraction returned no result');
                }
            } catch (directError) {
                console.error('Direct extraction failed:', directError);
            }
            
            // If direct extraction didn't work, fall back to URL method immediately
            if (!extractionSuccess) {
                clearTimeout(redirectTimeout);
                console.log('Content extraction unavailable, using URL method');
                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                showStatus('info', 'Opening News Checker...');
                chrome.tabs.create({ url: analyzeUrl });
                setTimeout(() => window.close(), 500);
                extractionSuccess = true;
            }
            
            /* Disabled message method - less reliable than direct extraction
            if (false) {
                // Fallback: Try content script message method (disabled - less reliable)
                try {
                    chrome.tabs.sendMessage(tab.id, { action: 'extractContent' }, (response) => {
                    if (chrome.runtime.lastError || !response || !response.success) {
                        // Fallback to URL method
                        console.log('Message method failed, using URL fallback');
                        const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                        showStatus('success', 'Opening News Checker...');
                        chrome.tabs.create({ url: analyzeUrl });
                        setTimeout(() => window.close(), 500);
                        return;
                    }
                    
                    if (response.data && response.data.content && response.data.content.length > 50) {
                        const contentData = {
                            url: response.data.url,
                            title: response.data.title,
                            content: response.data.content
                        };
                        
                        // Use Unicode-safe base64 encoding
                        const jsonString = JSON.stringify(contentData);
                        const encoded = btoa(unescape(encodeURIComponent(jsonString)));
                        const fullUrl = `${streamlitUrl}?content=${encodeURIComponent(encoded)}`;
                        
                        // Check URL length
                        if (fullUrl.length > 2000) {
                            // URL too long - truncate or use URL method
                            const maxContentLength = Math.floor(response.data.content.length * 0.8);
                            contentData.content = response.data.content.substring(0, maxContentLength) + '\n\n[Content truncated due to URL length limit.]';
                            
                            const truncatedJson = JSON.stringify(contentData);
                            const truncatedEncoded = btoa(unescape(encodeURIComponent(truncatedJson)));
                            const truncatedUrl = `${streamlitUrl}?content=${encodeURIComponent(truncatedEncoded)}`;
                            
                            if (truncatedUrl.length <= 2000) {
                                showStatus('warning', 'Content truncated. Opening News Checker...');
                                chrome.tabs.create({ url: truncatedUrl });
                            } else {
                                showStatus('info', 'Content too long, using URL method...');
                                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                                chrome.tabs.create({ url: analyzeUrl });
                            }
                        } else {
                            showStatus('success', 'Content extracted! Opening News Checker...');
                            chrome.tabs.create({ url: fullUrl });
                        }
                        setTimeout(() => window.close(), 500);
                    } else {
                        // Fallback to URL method
                        const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                        showStatus('success', 'Opening News Checker...');
                        chrome.tabs.create({ url: analyzeUrl });
                        setTimeout(() => window.close(), 500);
                    }
                });
            } catch (messageError) {
                // Final fallback to URL method
                console.log('All methods failed, using URL fallback');
                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                showStatus('success', 'Opening News Checker...');
                chrome.tabs.create({ url: analyzeUrl });
                setTimeout(() => window.close(), 500);
            }
            
        } catch (error) {
            console.error('Extension error:', error);
            showStatus('error', 'Error: ' + error.message);
            // Always fall back to URL method - ensure redirect happens
            try {
                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                showStatus('info', 'Opening News Checker (fallback)...');
                chrome.tabs.create({ url: analyzeUrl });
                setTimeout(() => window.close(), 500);
            } catch (e) {
                console.error('Fallback also failed:', e);
                showStatus('error', 'Failed to open Streamlit. Please check URL settings.');
            }
        }
    });
    
    // Copy URL button
    document.getElementById('copyBtn').addEventListener('click', async () => {
        if (!currentUrl) {
            showStatus('error', 'No URL to copy');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(currentUrl);
            showStatus('success', 'URL copied to clipboard!');
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = currentUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showStatus('success', 'URL copied to clipboard!');
        }
    });
});

function showStatus(type, message) {
    const statusDiv = document.getElementById('status');
    statusDiv.className = `status ${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}


// Default Streamlit app URL (user can change this)
const DEFAULT_STREAMLIT_URL = 'https://newsfactchecker.streamlit.app';

// Function to extract content directly (runs in page context)
// This is the PRIMARY method - extracts content from live page to bypass 403 errors
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
        'meta[name="title"]',
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
    
    // AGGRESSIVE content extraction - try many selectors and get the best one
    const contentSelectors = [
        'article',
        '[role="article"]',
        'main article',
        'main [role="article"]',
        '.article-content',
        '.article-body',
        '.article-text',
        '.article-main',
        '.post-content',
        '.story-body',
        '.story-content',
        '.content-body',
        '.entry-content',
        '.news-content',
        '.news-body',
        '.article',
        '.story',
        '.news-article',
        '[class*="article"]',
        '[class*="story"]',
        '[class*="content"]',
        '[class*="post"]',
        '[id*="article"]',
        '[id*="content"]',
        '[id*="story"]',
        '[id*="post"]',
        'main',
        '[role="main"]'
    ];
    
    let bestContent = '';
    let bestLength = 0;
    
    // Try all selectors and keep the one with most content
    for (const selector of contentSelectors) {
        try {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                // Get text content
                const text = el.innerText || el.textContent || '';
                const textLength = text.trim().length;
                
                // Prefer longer content, but accept anything > 50 chars
                if (textLength > bestLength && textLength > 50) {
                    bestContent = text;
                    bestLength = textLength;
                }
            }
        } catch(e) {}
    }
    
    // If we found good content, use it
    if (bestContent && bestLength > 50) {
        result.content = bestContent;
    } else {
        // FALLBACK: Get body text but aggressively filter out non-content
        const body = document.body;
        if (body) {
            const clone = body.cloneNode(true);
            
            // Remove ALL non-content elements aggressively
            const removeSelectors = [
                'nav', 'header', 'footer', 'aside', 'script', 'style', 'iframe',
                'noscript', 'svg', 'canvas', 'video', 'audio', 'embed', 'object',
                '.nav', '.navigation', '.menu', '.sidebar', '.ad', '.advertisement',
                '.social', '.share', '.comment', '.related', '.recommended',
                '.trending', '.newsletter', '.subscribe', '.cookie', '.consent',
                '.header', '.footer', '.menu', '.sidebar', '.widget',
                '[class*="nav"]', '[class*="menu"]', '[class*="ad"]',
                '[class*="social"]', '[class*="share"]', '[class*="widget"]',
                '[id*="nav"]', '[id*="menu"]', '[id*="ad"]', '[id*="sidebar"]',
                '[role="navigation"]', '[role="banner"]', '[role="complementary"]',
                '[role="search"]', '[role="form"]'
            ];
            
            removeSelectors.forEach(sel => {
                try {
                    clone.querySelectorAll(sel).forEach(el => el.remove());
                } catch(e) {}
            });
            
            // Try to get paragraphs first (most reliable)
            const paragraphs = clone.querySelectorAll('p');
            if (paragraphs.length > 3) {
                const paraTexts = [];
                paragraphs.forEach(p => {
                    const text = (p.innerText || p.textContent || '').trim();
                    // Keep paragraphs that are substantial and not navigation
                    if (text.length > 30 && 
                        !text.match(/^(cookie|subscribe|follow|menu|home|about|contact|skip|jump|login|sign)/i) &&
                        !text.match(/^(click|read more|share|like|comment)/i)) {
                        paraTexts.push(text);
                    }
                });
                if (paraTexts.length > 0) {
                    result.content = paraTexts.join('\n\n');
                }
            }
            
            // If paragraphs didn't work, get all text
            if (!result.content || result.content.length < 100) {
                const allText = clone.innerText || clone.textContent || '';
                if (allText && allText.trim().length > 50) {
                    result.content = allText;
                }
            }
        }
    }
    
    // Clean up content - aggressive filtering
    if (result.content) {
        result.content = result.content
            .replace(/\n{3,}/g, '\n\n')  // Max 2 newlines
            .replace(/[ \t]{2,}/g, ' ')   // Multiple spaces to single
            .replace(/^\s+|\s+$/gm, '')   // Trim each line
            .trim();
        
        // Remove very short lines and navigation-like text
        const lines = result.content.split('\n');
        const filteredLines = lines.filter(line => {
            const trimmed = line.trim();
            // Keep lines that are substantial or important
            return trimmed.length > 15 || 
                   trimmed.match(/^[A-Z][^.!?]*[.!?]$/) || // Complete sentences
                   !trimmed.match(/^(cookie|subscribe|follow|menu|home|about|contact|skip|jump|login|sign|click|read more|share|like|comment|advertisement|ad|sponsored)/i);
        });
        result.content = filteredLines.join('\n').trim();
    }
    
    // Final check - ensure we have some content
    if (!result.content || result.content.length < 20) {
        // Last resort: get any text from body
        try {
            const bodyText = document.body.innerText || document.body.textContent || '';
            if (bodyText && bodyText.trim().length > 20) {
                result.content = bodyText.trim().substring(0, 5000); // Limit to 5000 chars
            }
        } catch(e) {}
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
                    
                    // ACCEPT ANY CONTENT - even if very short (minimum 10 chars)
                    // This ensures we always send extracted content instead of falling back to URL (which causes 403)
                    if (articleData && articleData.content && typeof articleData.content === 'string' && contentLength > 10) {
                        const contentData = {
                            url: articleData.url || currentUrl || '',
                            title: articleData.title || 'Untitled Article',
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
                            const maxContentLength = Math.floor(contentLength * 0.8);
                            if (typeof articleData.content === 'string') {
                                contentData.content = articleData.content.substring(0, maxContentLength) + '\n\n[Content truncated due to URL length limit. Full content available on source page.]';
                            } else {
                                throw new Error('Content is not a string');
                            }
                            
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
                                // Still too long - truncate more aggressively (50% instead of 80%)
                                clearTimeout(redirectTimeout);
                                console.log('Even truncated URL too long, truncating more aggressively...');
                                const aggressiveMaxLength = Math.floor(contentLength * 0.5);
                                if (typeof articleData.content === 'string') {
                                    contentData.content = articleData.content.substring(0, aggressiveMaxLength) + '\n\n[Content significantly truncated due to URL length limit. Please visit the source page for full content.]';
                                    const aggressiveJson = JSON.stringify(contentData);
                                    const aggressiveEncoded = btoa(unescape(encodeURIComponent(aggressiveJson)));
                                    const aggressiveUrl = `${streamlitUrl}?content=${encodeURIComponent(aggressiveEncoded)}`;
                                    
                                    if (aggressiveUrl.length <= 2000) {
                                        showStatus('warning', 'Content heavily truncated. Opening News Checker...');
                                        chrome.tabs.create({ url: aggressiveUrl });
                                        setTimeout(() => window.close(), 500);
                                        extractionSuccess = true;
                                        return;
                                    }
                                }
                                // If still too long, send just the first 1000 chars
                                console.log('Content extremely long, sending first 1000 chars only');
                                contentData.content = (typeof articleData.content === 'string' ? articleData.content.substring(0, 1000) : '') + '\n\n[Content truncated - first 1000 characters only. Visit source for full content.]';
                                const minimalJson = JSON.stringify(contentData);
                                const minimalEncoded = btoa(unescape(encodeURIComponent(minimalJson)));
                                const minimalUrl = `${streamlitUrl}?content=${encodeURIComponent(minimalEncoded)}`;
                                showStatus('warning', 'Sending partial content. Opening News Checker...');
                                chrome.tabs.create({ url: minimalUrl });
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
                        // Content too short - but still try to send it (better than URL method which causes 403)
                        console.log('Extraction returned short content, but sending anyway to avoid 403:', {
                            hasContent: !!(articleData && articleData.content),
                            length: contentLength,
                            type: articleData && articleData.content ? typeof articleData.content : 'undefined'
                        });
                        
                        // Send even short content - it's better than nothing
                        if (articleData && articleData.content && typeof articleData.content === 'string' && contentLength > 0) {
                            const shortContentData = {
                                url: articleData.url || currentUrl || '',
                                title: articleData.title || 'Untitled Article',
                                content: articleData.content + '\n\n[Note: Limited content extracted. Please check the source page for full article.]'
                            };
                            
                            const shortJson = JSON.stringify(shortContentData);
                            const shortEncoded = btoa(unescape(encodeURIComponent(shortJson)));
                            const shortUrl = `${streamlitUrl}?content=${encodeURIComponent(shortEncoded)}`;
                            
                            clearTimeout(redirectTimeout);
                            showStatus('warning', 'Limited content extracted. Opening News Checker...');
                            chrome.tabs.create({ url: shortUrl });
                            setTimeout(() => window.close(), 500);
                            extractionSuccess = true;
                            return;
                        }
                    }
                } else {
                    console.log('Extraction returned no result');
                }
            } catch (directError) {
                console.error('Direct extraction failed:', directError);
            }
            
            // ONLY fall back to URL method if extraction completely failed
            // This should rarely happen since we accept even very short content
            if (!extractionSuccess) {
                clearTimeout(redirectTimeout);
                console.log('Content extraction completely failed, using URL method (may hit 403)');
                showStatus('error', 'Could not extract content. Using URL method (may fail on some sites)...');
                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                chrome.tabs.create({ url: analyzeUrl });
                setTimeout(() => window.close(), 500);
                extractionSuccess = true;
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


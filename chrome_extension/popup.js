// Default Streamlit app URL (user can change this)
const DEFAULT_STREAMLIT_URL = 'https://newsfactchecker.streamlit.app';

// Function to extract content directly (runs in page context)
function extractContentDirectly() {
    const result = {
        url: window.location.href,
        title: '',
        content: ''
    };
    
    // Extract title
    const titleSelectors = ['h1', '[property="og:title"]', '[name="twitter:title"]', 'title'];
    for (const selector of titleSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            result.title = element.textContent || element.content || element.innerText || '';
            if (result.title) break;
        }
    }
    
    // Try to extract main article content
    const contentSelectors = [
        'article', '[role="article"]', '.article-content', '.article-body',
        '.post-content', '.story-body', '.content-body', '.entry-content',
        'main article', '.article', '.story', '.news-article'
    ];
    
    let articleElement = null;
    for (const selector of contentSelectors) {
        articleElement = document.querySelector(selector);
        if (articleElement) break;
    }
    
    if (articleElement) {
        result.content = articleElement.innerText || articleElement.textContent || '';
    } else {
        // Fallback: get body text but filter out navigation
        const body = document.body;
        if (body) {
            const clone = body.cloneNode(true);
            const removeSelectors = ['nav', 'header', 'footer', 'aside', 'script', 'style',
                                   '.nav', '.navigation', '.menu', '.sidebar', '.ad',
                                   '.advertisement', '.social', '.share', '.comment'];
            removeSelectors.forEach(sel => {
                try {
                    clone.querySelectorAll(sel).forEach(el => el.remove());
                } catch(e) {}
            });
            result.content = clone.innerText || clone.textContent || '';
        }
    }
    
    // Clean up content
    if (result.content) {
        result.content = result.content
            .replace(/\n{3,}/g, '\n\n')
            .replace(/[ \t]{2,}/g, ' ')
            .trim();
    }
    
    return result;
}

// Get current tab URL
document.addEventListener('DOMContentLoaded', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentUrl = tab.url;
    
    // Display current URL
    const urlDisplay = document.getElementById('currentUrl');
    urlDisplay.textContent = currentUrl || 'No URL found';
    
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
            
            // First, try to inject content script if not already injected
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.js']
                });
            } catch (injectError) {
                // Script might already be injected, that's okay
                console.log('Script injection note:', injectError.message);
            }
            
            // Wait a moment for script to initialize
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Try direct extraction first (more reliable)
            try {
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: extractContentDirectly
                });
                
                if (results && results[0] && results[0].result) {
                    const articleData = results[0].result;
                    
                    if (articleData.content && articleData.content.length > 50) {
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
                                showStatus('warning', 'Content truncated due to length. Opening News Checker...');
                                chrome.tabs.create({ url: truncatedUrl });
                                setTimeout(() => window.close(), 500);
                                return;
                            } else {
                                // Still too long, fall back to URL method
                                console.log('Even truncated URL too long, using URL method');
                                showStatus('info', 'Content too long, using URL method...');
                                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                                chrome.tabs.create({ url: analyzeUrl });
                                setTimeout(() => window.close(), 500);
                                return;
                            }
                        }
                        
                        showStatus('success', 'Content extracted! Opening News Checker...');
                        chrome.tabs.create({ url: fullUrl });
                        setTimeout(() => window.close(), 500);
                        return;
                    }
                }
            } catch (directError) {
                console.log('Direct extraction failed, trying message method:', directError);
            }
            
            // Fallback: Try content script message method
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
                        const analyzeUrl = `${streamlitUrl}?content=${encodeURIComponent(encoded)}`;
                        
                        showStatus('success', 'Content extracted! Opening News Checker...');
                        chrome.tabs.create({ url: analyzeUrl });
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
            showStatus('error', 'Error: ' + error.message);
            // Fallback to URL method
            try {
                const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                chrome.tabs.create({ url: analyzeUrl });
            } catch (e) {
                console.error('Fallback also failed:', e);
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


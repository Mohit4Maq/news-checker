// Default Streamlit app URL (user can change this)
const DEFAULT_STREAMLIT_URL = 'https://newsfactchecker.streamlit.app';

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
            
            // Send message to content script to extract content
            chrome.tabs.sendMessage(tab.id, { action: 'extractContent' }, async (response) => {
                if (chrome.runtime.lastError) {
                    // Content script might not be injected, fallback to URL method
                    console.log('Content script not available, using URL method');
                    const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                    chrome.tabs.create({ url: analyzeUrl });
                    showStatus('success', 'Opening News Checker...');
                    setTimeout(() => window.close(), 1000);
                    return;
                }
                
                if (response && response.success && response.data) {
                    const articleData = response.data;
                    
                    // Check if we got meaningful content
                    if (articleData.content && articleData.content.length > 50) {
                        // Send content to Streamlit via URL parameter (base64 encoded)
                        // Streamlit will decode and use it
                        const contentData = {
                            url: articleData.url,
                            title: articleData.title,
                            content: articleData.content
                        };
                        
                        // Encode as base64 to pass via URL
                        const encoded = btoa(JSON.stringify(contentData));
                        const analyzeUrl = `${streamlitUrl}?content=${encodeURIComponent(encoded)}`;
                        
                        chrome.tabs.create({ url: analyzeUrl });
                        showStatus('success', 'Content extracted! Opening News Checker...');
                    } else {
                        // Fallback to URL method if content extraction failed
                        showStatus('warning', 'Could not extract content, using URL method...');
                        const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                        chrome.tabs.create({ url: analyzeUrl });
                    }
                } else {
                    // Fallback to URL method
                    showStatus('warning', 'Extraction failed, using URL method...');
                    const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
                    chrome.tabs.create({ url: analyzeUrl });
                }
                
                setTimeout(() => {
                    window.close();
                }, 1500);
            });
            
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


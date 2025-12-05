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
        document.getElementById('streamlitUrl').value = streamlitUrl;
    });
    
    // Save Streamlit URL when changed
    document.getElementById('streamlitUrl').addEventListener('change', (e) => {
        chrome.storage.sync.set({ streamlitUrl: e.target.value });
    });
    
    // Analyze button
    document.getElementById('analyzeBtn').addEventListener('click', async () => {
        const streamlitUrl = document.getElementById('streamlitUrl').value || DEFAULT_STREAMLIT_URL;
        const statusDiv = document.getElementById('status');
        
        if (!currentUrl || !currentUrl.startsWith('http')) {
            showStatus('error', 'Invalid URL. Please navigate to a news article.');
            return;
        }
        
        if (!streamlitUrl || streamlitUrl === DEFAULT_STREAMLIT_URL) {
            showStatus('error', 'Please set your Streamlit app URL in the settings above.');
            return;
        }
        
        try {
            // Open Streamlit app with URL parameter
            const analyzeUrl = `${streamlitUrl}?url=${encodeURIComponent(currentUrl)}`;
            chrome.tabs.create({ url: analyzeUrl });
            
            showStatus('success', 'Opening News Checker...');
            
            // Close popup after a short delay
            setTimeout(() => {
                window.close();
            }, 1000);
        } catch (error) {
            showStatus('error', 'Error: ' + error.message);
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


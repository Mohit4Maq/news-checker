// Content script - extracts article content from the page
// This runs in the page context, so it can read content even if site blocks automated requests

// Function to extract article content from the page
function extractArticleContent() {
    const result = {
        url: window.location.href,
        title: '',
        content: '',
        html: ''
    };
    
    // Extract title
    const titleSelectors = [
        'h1',
        '[property="og:title"]',
        '[name="twitter:title"]',
        'title'
    ];
    
    for (const selector of titleSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            result.title = element.textContent || element.content || element.innerText || '';
            if (result.title) break;
        }
    }
    
    // Try to extract main article content
    const contentSelectors = [
        'article',
        '[role="article"]',
        '.article-content',
        '.article-body',
        '.post-content',
        '.story-body',
        '.content-body',
        '.entry-content',
        'main article',
        '.article',
        '.story',
        '.news-article'
    ];
    
    let articleElement = null;
    for (const selector of contentSelectors) {
        articleElement = document.querySelector(selector);
        if (articleElement) break;
    }
    
    if (articleElement) {
        // Get text content (cleaner)
        result.content = articleElement.innerText || articleElement.textContent || '';
        // Also get HTML for better parsing if needed
        result.html = articleElement.innerHTML || '';
    } else {
        // Fallback: get body text but filter out navigation
        const body = document.body;
        if (body) {
            // Clone to avoid modifying original
            const clone = body.cloneNode(true);
            
            // Remove common non-content elements
            const removeSelectors = ['nav', 'header', 'footer', 'aside', 'script', 'style', 
                                   '.nav', '.navigation', '.menu', '.sidebar', '.ad', 
                                   '.advertisement', '.social', '.share', '.comment'];
            removeSelectors.forEach(sel => {
                try {
                    clone.querySelectorAll(sel).forEach(el => el.remove());
                } catch(e) {}
            });
            
            result.content = clone.innerText || clone.textContent || '';
            result.html = clone.innerHTML || '';
        }
    }
    
    // Clean up content - remove extra whitespace
    if (result.content) {
        result.content = result.content
            .replace(/\n{3,}/g, '\n\n')  // Max 2 newlines
            .replace(/[ \t]{2,}/g, ' ')   // Multiple spaces to single
            .trim();
    }
    
    return result;
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractContent') {
        try {
            const content = extractArticleContent();
            sendResponse({ success: true, data: content });
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
        return true; // Keep channel open for async response
    }
});

// Detect if page is a news article (optional enhancement)
function detectNewsArticle() {
    // Check for common news article indicators
    const articleSelectors = [
        'article',
        '[role="article"]',
        '.article',
        '.story',
        '.news-article'
    ];
    
    for (const selector of articleSelectors) {
        if (document.querySelector(selector)) {
            return true;
        }
    }
    
    return false;
}

// Optional: Add visual indicator on news pages
if (detectNewsArticle()) {
    console.log('News article detected - extension ready to extract content');
}


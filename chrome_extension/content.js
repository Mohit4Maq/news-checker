// Content script - can add context menu or page detection here if needed
// For now, the popup handles everything

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
    // Could add a floating button or badge here
    console.log('News article detected');
}


#!/bin/bash

# Script to help create screenshots for Chrome Web Store
# This opens the HTML templates in your browser for easy screenshot capture

echo "📸 Chrome Web Store Screenshot Helper"
echo "======================================"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    echo ""
    echo "Opening HTML templates in your browser..."
    echo ""
    
    # Open promotional tile template
    if [ -f "promotional_tile.html" ]; then
        echo "1. Opening promotional tile template..."
        open promotional_tile.html
        echo "   → Take screenshot at 440x280 pixels"
        echo "   → Use browser dev tools: Cmd+Option+I, then toggle device toolbar"
        echo ""
    fi
    
    # Open screenshot template
    if [ -f "screenshot_template.html" ]; then
        echo "2. Opening screenshot template..."
        open screenshot_template.html
        echo "   → Take screenshot at 1280x800 pixels"
        echo "   → Customize content, then screenshot"
        echo ""
    fi
    
    echo "📋 Instructions:"
    echo "   1. Use browser dev tools (Cmd+Option+I)"
    echo "   2. Toggle device toolbar (Cmd+Shift+M)"
    echo "   3. Set custom dimensions:"
    echo "      - Promotional tile: 440 x 280"
    echo "      - Screenshots: 1280 x 800"
    echo "   4. Take screenshot (Cmd+Shift+4, then Space, then click window)"
    echo "   5. Or use browser's screenshot tool"
    echo ""
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    echo ""
    echo "Opening HTML templates..."
    xdg-open promotional_tile.html 2>/dev/null || echo "Please open promotional_tile.html manually"
    xdg-open screenshot_template.html 2>/dev/null || echo "Please open screenshot_template.html manually"
    
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 Detected Windows"
    echo ""
    echo "Opening HTML templates..."
    start promotional_tile.html
    start screenshot_template.html
    
else
    echo "❓ Unknown OS. Please open these files manually:"
    echo "   - promotional_tile.html"
    echo "   - screenshot_template.html"
fi

echo ""
echo "✅ Alternative: Use online tools like Canva.com"
echo "   - Free templates available"
echo "   - Easy drag-and-drop interface"
echo "   - Export at exact dimensions"
echo ""
echo "📖 See PROMOTIONAL_IMAGES_GUIDE.md for detailed instructions"


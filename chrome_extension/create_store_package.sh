#!/bin/bash

# Script to create Chrome Web Store package
# This creates a ZIP file with only the necessary files for submission

echo "📦 Creating Chrome Web Store package..."

# Navigate to extension directory
cd "$(dirname "$0")"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "📁 Using temp directory: $TEMP_DIR"

# Copy necessary files
echo "📋 Copying files..."
cp manifest.json "$TEMP_DIR/"
cp popup.html "$TEMP_DIR/"
cp popup.js "$TEMP_DIR/"
cp content.js "$TEMP_DIR/"

# Copy icons directory
echo "🖼️  Copying icons..."
mkdir -p "$TEMP_DIR/icons"
cp icons/*.png "$TEMP_DIR/icons/"

# Create ZIP file
ZIP_NAME="../news-checker-extension-v$(grep -oP '"version":\s*"\K[^"]+' manifest.json).zip"
echo "📦 Creating ZIP: $ZIP_NAME"

cd "$TEMP_DIR"
zip -r "$OLDPWD/$ZIP_NAME" . -q

# Cleanup
cd "$OLDPWD"
rm -rf "$TEMP_DIR"

echo "✅ Package created: $ZIP_NAME"
echo ""
echo "📋 Files included:"
unzip -l "$ZIP_NAME" | grep -E "\.(json|html|js|png)$"

echo ""
echo "✅ Ready for Chrome Web Store submission!"
echo "📤 Upload this file at: https://chrome.google.com/webstore/devconsole"


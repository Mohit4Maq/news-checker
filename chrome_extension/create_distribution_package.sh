#!/bin/bash
# Create a clean distribution package for the Chrome extension
# This includes only essential files needed for installation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
VERSION=$(grep '"version"' manifest.json | cut -d'"' -f4)
PACKAGE_NAME="news-checker-extension-v${VERSION}"
DIST_DIR="../dist"

echo "📦 Creating distribution package for News Checker Extension v${VERSION}..."

# Create dist directory
mkdir -p "${DIST_DIR}/${PACKAGE_NAME}"

# Copy essential files
echo "📋 Copying essential files..."
cp manifest.json "${DIST_DIR}/${PACKAGE_NAME}/"
cp popup.html "${DIST_DIR}/${PACKAGE_NAME}/"
cp popup.js "${DIST_DIR}/${PACKAGE_NAME}/"
cp content.js "${DIST_DIR}/${PACKAGE_NAME}/"

# Copy icons directory
echo "🎨 Copying icons..."
cp -r icons "${DIST_DIR}/${PACKAGE_NAME}/"

# Copy helpful documentation
echo "📚 Copying documentation..."
cp README.md "${DIST_DIR}/${PACKAGE_NAME}/" 2>/dev/null || true
cp install_instructions.md "${DIST_DIR}/${PACKAGE_NAME}/" 2>/dev/null || true

# Create ZIP file
echo "📦 Creating ZIP archive..."
cd "${DIST_DIR}"
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" -q

# Clean up temp directory (optional - comment out if you want to keep it)
# rm -rf "${PACKAGE_NAME}"

echo ""
echo "✅ Distribution package created!"
echo "📁 Location: ${DIST_DIR}/${PACKAGE_NAME}.zip"
echo "📦 Package name: ${PACKAGE_NAME}.zip"
echo ""
echo "📋 Files included:"
echo "   - manifest.json"
echo "   - popup.html"
echo "   - popup.js"
echo "   - content.js"
echo "   - icons/ (all icon files)"
echo "   - README.md (if available)"
echo "   - install_instructions.md (if available)"
echo ""
echo "🚀 Share this ZIP file with users for manual installation!"


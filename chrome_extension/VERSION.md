# Extension Version History

## Version 1.1.0 (2025-12-05)
- ✅ Added programmatic content script injection
- ✅ Added direct extraction function as fallback
- ✅ Added "scripting" permission for better content extraction
- ✅ Improved error handling for content extraction
- ✅ Solves 403 errors by reading content from user's browser

## Version 1.0.0 (2025-12-05)
- ✅ Initial release
- ✅ Basic URL parameter passing
- ✅ Streamlit app integration
- ✅ Manual paste fallback

## Version Update Guidelines

When updating the extension:
1. Update version in `manifest.json`
2. Update version in `popup.html` (if displayed)
3. Update this VERSION.md file
4. Use semantic versioning:
   - MAJOR.MINOR.PATCH
   - MAJOR: Breaking changes
   - MINOR: New features, backwards compatible
   - PATCH: Bug fixes, backwards compatible


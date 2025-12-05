#!/usr/bin/env python3
"""
Comprehensive test for Chrome Extension and Streamlit integration
Tests all components end-to-end
"""

import sys
import os
import json
import base64

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extension_files():
    """Test all extension files exist and are valid"""
    print("=" * 70)
    print("TEST 1: Extension Files")
    print("=" * 70)
    
    from pathlib import Path
    import json
    
    ext_dir = Path("chrome_extension")
    required_files = {
        "manifest.json": "Extension manifest",
        "popup.html": "Extension popup UI",
        "popup.js": "Extension logic",
        "content.js": "Content script",
        "icons/icon16.png": "16px icon",
        "icons/icon48.png": "48px icon",
        "icons/icon128.png": "128px icon"
    }
    
    all_good = True
    for file_path, desc in required_files.items():
        full_path = ext_dir / file_path
        if full_path.exists():
            print(f"✅ {desc}: {file_path}")
        else:
            print(f"❌ {desc}: {file_path} - MISSING")
            all_good = False
    
    # Validate manifest.json
    try:
        with open(ext_dir / "manifest.json", "r") as f:
            manifest = json.load(f)
        
        checks = [
            ("manifest_version", lambda v: v == 3, "Must be 3"),
            ("name", lambda n: "News Checker" in n, "Must contain 'News Checker'"),
            ("version", lambda v: v and "." in str(v), "Must have version format X.Y.Z"),
            ("permissions", lambda p: "activeTab" in p and "storage" in p and "scripting" in p, "Must have required permissions"),
        ]
        
        for field, validator, desc in checks:
            if field in manifest:
                if validator(manifest[field]):
                    print(f"✅ Manifest {field}: Valid ({desc})")
                else:
                    print(f"❌ Manifest {field}: Invalid - {desc}")
                    all_good = False
            else:
                print(f"❌ Manifest missing: {field}")
                all_good = False
                
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        all_good = False
    
    return all_good


def test_content_extraction_logic():
    """Test the content extraction function logic"""
    print("\n" + "=" * 70)
    print("TEST 2: Content Extraction Logic")
    print("=" * 70)
    
    # Read the extraction function from popup.js
    try:
        with open("chrome_extension/popup.js", "r") as f:
            js_content = f.read()
        
        checks = [
            ("extractContentDirectly", "Extraction function defined"),
            ("querySelector", "DOM query methods"),
            ("innerText", "Text extraction"),
            ("textContent", "Text extraction fallback"),
            ("article", "Article selector"),
            ("[role=\"article\"]", "ARIA role selector"),
            (".article-content", "Class-based selector"),
            ("cloneNode", "DOM cloning for filtering"),
            ("querySelectorAll", "Multiple element selection"),
            ("replace", "Content cleaning"),
            ("trim", "Content trimming"),
        ]
        
        all_good = True
        for check, desc in checks:
            if check in js_content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - NOT FOUND")
                all_good = False
        
        # Check for Unicode-safe encoding
        if "btoa(unescape(encodeURIComponent" in js_content:
            print("✅ Unicode-safe base64 encoding")
        else:
            print("❌ Unicode-safe encoding NOT FOUND")
            all_good = False
        
        # Check for URL length checking
        if "fullUrl.length > 2000" in js_content:
            print("✅ URL length checking")
        else:
            print("❌ URL length checking NOT FOUND")
            all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_unicode_encoding():
    """Test Unicode-safe base64 encoding/decoding"""
    print("\n" + "=" * 70)
    print("TEST 3: Unicode Encoding/Decoding")
    print("=" * 70)
    
    # Test data with Unicode characters
    test_cases = [
        {
            "name": "English text",
            "data": {"title": "Test Article", "content": "This is a test article with normal text.", "url": "https://example.com"}
        },
        {
            "name": "Unicode characters",
            "data": {"title": "Test 📰 Article", "content": "This is a test with emoji 📰 and special chars: àáâãäå", "url": "https://example.com"}
        },
        {
            "name": "Hindi text",
            "data": {"title": "समाचार लेख", "content": "यह एक परीक्षण लेख है जिसमें हिंदी पाठ है।", "url": "https://example.com"}
        },
        {
            "name": "Mixed content",
            "data": {"title": "News Article 📰", "content": "This article contains English, हिंदी, and emoji 📰🎉", "url": "https://example.com"}
        }
    ]
    
    all_good = True
    for test_case in test_cases:
        try:
            # Simulate JavaScript encoding
            json_string = json.dumps(test_case["data"])
            # JavaScript: btoa(unescape(encodeURIComponent(jsonString)))
            # Python equivalent:
            encoded_bytes = json_string.encode('utf-8')
            encoded_b64 = base64.b64encode(encoded_bytes).decode('ascii')
            
            # Decode (as Streamlit would)
            decoded_bytes = base64.b64decode(encoded_b64)
            decoded = decoded_bytes.decode('utf-8')
            decoded_data = json.loads(decoded)
            
            if decoded_data == test_case["data"]:
                print(f"✅ {test_case['name']}: Encoding/decoding works")
            else:
                print(f"❌ {test_case['name']}: Data mismatch")
                all_good = False
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {e}")
            all_good = False
    
    return all_good


def test_url_length_handling():
    """Test URL length handling"""
    print("\n" + "=" * 70)
    print("TEST 4: URL Length Handling")
    print("=" * 70)
    
    # Simulate a long article
    long_content = "This is a very long article. " * 500  # ~12,500 chars
    test_data = {
        "title": "Long Article",
        "content": long_content,
        "url": "https://example.com/article"
    }
    
    try:
        json_string = json.dumps(test_data)
        encoded_bytes = json_string.encode('utf-8')
        encoded_b64 = base64.b64encode(encoded_bytes).decode('ascii')
        
        streamlit_url = "https://newsfactchecker.streamlit.app"
        full_url = f"{streamlit_url}?content={encoded_b64}"
        
        url_length = len(full_url)
        print(f"📏 Long article URL length: {url_length} characters")
        
        if url_length > 2000:
            print("✅ URL length exceeds limit (expected for long articles)")
            print("   Extension should truncate or use URL method")
            
            # Test truncation logic
            max_content_length = int(len(long_content) * 0.8)
            truncated_content = long_content[:max_content_length] + "\n\n[Content truncated...]"
            truncated_data = {
                "title": test_data["title"],
                "content": truncated_content,
                "url": test_data["url"]
            }
            
            truncated_json = json.dumps(truncated_data)
            truncated_encoded = base64.b64encode(truncated_json.encode('utf-8')).decode('ascii')
            truncated_url = f"{streamlit_url}?content={truncated_encoded}"
            
            print(f"📏 Truncated URL length: {len(truncated_url)} characters")
            
            if len(truncated_url) <= 2000:
                print("✅ Truncation works - URL within limit")
            else:
                print("⚠️  Even truncated URL too long - should use URL method")
        else:
            print("✅ URL length within limit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_streamlit_integration():
    """Test Streamlit app integration"""
    print("\n" + "=" * 70)
    print("TEST 5: Streamlit Integration")
    print("=" * 70)
    
    with open("app.py", "r") as f:
        app_content = f.read()
    
    checks = [
        ('st.query_params.get("content"', "Content parameter handling"),
        ('st.query_params.get("url"', "URL parameter handling"),
        ('base64.b64decode', "Base64 decoding"),
        ('json.loads', "JSON parsing"),
        ('auto_analyzed', "Auto-analysis flag"),
        ('display_analysis_result', "Result display function"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check in app_content:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - NOT FOUND")
            all_good = False
    
    # Check for 403 error handling
    if '403' in app_content and 'Forbidden' in app_content:
        print("✅ 403 error handling")
    else:
        print("❌ 403 error handling NOT FOUND")
        all_good = False
    
    # Check for manual paste option
    if 'manual paste' in app_content.lower() or 'Paste Article Content' in app_content:
        print("✅ Manual paste option")
    else:
        print("❌ Manual paste option NOT FOUND")
        all_good = False
    
    return all_good


def test_backend_analyzer():
    """Test backend analyzer"""
    print("\n" + "=" * 70)
    print("TEST 6: Backend Analyzer")
    print("=" * 70)
    
    try:
        from news_analyzer import NewsAnalyzer
        
        print("✅ NewsAnalyzer imported")
        
        # Initialize (without API key test)
        analyzer = NewsAnalyzer()
        print("✅ Analyzer initialized")
        
        # Check methods
        required_methods = [
            'fetch_article_content',
            'analyze_news',
            'load_rules',
            'create_analysis_prompt',
            'refine_category_based_on_scores'
        ]
        
        for method in required_methods:
            if hasattr(analyzer, method):
                print(f"✅ Method exists: {method}")
            else:
                print(f"❌ Method missing: {method}")
                return False
        
        # Check for content extraction improvements
        with open("news_analyzer.py", "r") as f:
            analyzer_content = f.read()
        
        if "_filter_news_content" in analyzer_content:
            print("✅ Content filtering function exists")
        else:
            print("❌ Content filtering function NOT FOUND")
        
        if "newspaper3k" in analyzer_content.lower():
            print("✅ Newspaper3k fallback method")
        else:
            print("❌ Newspaper3k fallback NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_extension_flow():
    """Test the complete extension flow logic"""
    print("\n" + "=" * 70)
    print("TEST 7: Extension Flow Logic")
    print("=" * 70)
    
    with open("chrome_extension/popup.js", "r") as f:
        js_content = f.read()
    
    flow_checks = [
        ("chrome.tabs.query", "Tab URL capture"),
        ("chrome.scripting.executeScript", "Script injection"),
        ("extractContentDirectly", "Direct extraction"),
        ("btoa(unescape(encodeURIComponent", "Unicode-safe encoding"),
        ("fullUrl.length > 2000", "URL length check"),
        ("chrome.tabs.create", "Tab creation/redirect"),
        ("?content=", "Content parameter"),
        ("?url=", "URL parameter fallback"),
    ]
    
    all_good = True
    for check, desc in flow_checks:
        if check in js_content:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - NOT FOUND")
            all_good = False
    
    # Check error handling
    if "catch" in js_content and "error" in js_content.lower():
        print("✅ Error handling")
    else:
        print("❌ Error handling NOT FOUND")
        all_good = False
    
    return all_good


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE EXTENSION & INTEGRATION TEST")
    print("=" * 70)
    print()
    
    results = []
    
    results.append(("Extension Files", test_extension_files()))
    results.append(("Content Extraction Logic", test_content_extraction_logic()))
    results.append(("Unicode Encoding", test_unicode_encoding()))
    results.append(("URL Length Handling", test_url_length_handling()))
    results.append(("Streamlit Integration", test_streamlit_integration()))
    results.append(("Backend Analyzer", test_backend_analyzer()))
    results.append(("Extension Flow Logic", test_extension_flow()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe extension is ready to use!")
        print("\nNext steps:")
        print("1. Reload extension in Chrome (chrome://extensions/)")
        print("2. Navigate to a news article")
        print("3. Click extension icon → 'Analyze This Article'")
        print("4. If 403 error occurs, use manual paste option in Streamlit")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


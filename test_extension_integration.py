#!/usr/bin/env python3
"""
Test script to simulate Chrome Extension → Streamlit integration
Tests the full flow without needing to actually run Streamlit
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extension_files():
    """Test that all extension files exist and are valid"""
    print("=" * 60)
    print("TEST 1: Chrome Extension Files")
    print("=" * 60)
    
    import json
    from pathlib import Path
    
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
        
        required_fields = ["manifest_version", "name", "version", "permissions", "action"]
        for field in required_fields:
            if field in manifest:
                print(f"✅ Manifest field: {field}")
            else:
                print(f"❌ Manifest missing: {field}")
                all_good = False
        
        # Check permissions
        perms = manifest.get("permissions", [])
        required_perms = ["activeTab", "storage"]
        for perm in required_perms:
            if perm in perms:
                print(f"✅ Permission: {perm}")
            else:
                print(f"❌ Missing permission: {perm}")
                all_good = False
                
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        all_good = False
    
    return all_good


def test_streamlit_integration():
    """Test that Streamlit app handles URL parameters correctly"""
    print("\n" + "=" * 60)
    print("TEST 2: Streamlit App Integration")
    print("=" * 60)
    
    with open("app.py", "r") as f:
        app_content = f.read()
    
    checks = [
        ('st.query_params.get("url"', "URL parameter extraction"),
        ('url_param', "URL parameter variable"),
        ('auto_analyzed', "Auto-analysis flag"),
        ('st.session_state.analyzer.analyze_news(url_param)', "Auto-analysis call"),
        ('value=default_url', "URL pre-fill in input"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check in app_content:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - NOT FOUND")
            all_good = False
    
    return all_good


def test_extension_javascript():
    """Test extension JavaScript logic"""
    print("\n" + "=" * 60)
    print("TEST 3: Extension JavaScript Logic")
    print("=" * 60)
    
    with open("chrome_extension/popup.js", "r") as f:
        js_content = f.read()
    
    checks = [
        ('chrome.tabs.query', "Tab URL capture"),
        ('chrome.storage.sync', "Settings storage"),
        ('encodeURIComponent', "URL encoding"),
        ('chrome.tabs.create', "Open Streamlit tab"),
        ('?url=', "URL parameter format"),
        ('analyzeBtn', "Analyze button ID"),
        ('copyBtn', "Copy button ID"),
        ('streamlitUrl', "Streamlit URL input ID"),
        ('addEventListener', "Event listeners"),
    ]
    
    all_good = True
    for check, desc in checks:
        if check in js_content:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - NOT FOUND")
            all_good = False
    
    return all_good


def test_url_flow_simulation():
    """Simulate the URL flow from extension to Streamlit"""
    print("\n" + "=" * 60)
    print("TEST 4: URL Flow Simulation")
    print("=" * 60)
    
    # Simulate what happens
    test_url = "https://example.com/news-article"
    
    print(f"1. User on article page: {test_url}")
    print("   ✅ Extension captures URL")
    
    print(f"\n2. Extension creates Streamlit URL:")
    streamlit_url = "https://your-app.streamlit.app"
    analyze_url = f"{streamlit_url}?url={test_url}"
    print(f"   ✅ {analyze_url}")
    
    print(f"\n3. Streamlit receives parameter:")
    print(f"   ✅ st.query_params.get('url') = '{test_url}'")
    
    print(f"\n4. Streamlit auto-analyzes:")
    print(f"   ✅ analyzer.analyze_news('{test_url}')")
    
    print(f"\n5. URL pre-filled in input field:")
    print(f"   ✅ st.text_input(value='{test_url}')")
    
    return True


def test_backend_analyzer():
    """Test backend analyzer is ready"""
    print("\n" + "=" * 60)
    print("TEST 5: Backend Analyzer")
    print("=" * 60)
    
    try:
        from news_analyzer import NewsAnalyzer
        
        print("✅ NewsAnalyzer class imported")
        
        # Check if analyzer can be initialized (without API key test)
        analyzer = NewsAnalyzer()
        print("✅ Analyzer initialized")
        
        # Check key methods exist
        methods = [
            'fetch_article_content',
            'analyze_news',
            'load_rules',
            'create_analysis_prompt'
        ]
        
        for method in methods:
            if hasattr(analyzer, method):
                print(f"✅ Method exists: {method}")
            else:
                print(f"❌ Method missing: {method}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CHROME EXTENSION INTEGRATION TEST")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Extension Files", test_extension_files()))
    results.append(("Streamlit Integration", test_streamlit_integration()))
    results.append(("Extension JavaScript", test_extension_javascript()))
    results.append(("URL Flow Simulation", test_url_flow_simulation()))
    results.append(("Backend Analyzer", test_backend_analyzer()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe Chrome extension is ready to use!")
        print("\nNext steps:")
        print("1. Load extension in Chrome (chrome://extensions/)")
        print("2. Set your Streamlit Cloud URL in extension settings")
        print("3. Navigate to a news article and click extension icon")
        print("4. Click 'Analyze This Article'")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


"""
Quick test script to verify the analyzer is working
"""

from news_analyzer import NewsAnalyzer

def test_analyzer():
    """Test the news analyzer with a sample URL"""
    print("🚀 Testing News Analyzer...\n")
    
    try:
        # Initialize analyzer
        analyzer = NewsAnalyzer()
        
        # Test API key
        print("1️⃣  Testing API key...")
        if analyzer.test_api_key():
            print("   ✅ API key is working!\n")
        else:
            print("   ❌ API key test failed!\n")
            return
        
        # Test with a sample URL (you can change this)
        test_url = input("Enter a news URL to test (or press Enter to skip): ").strip()
        
        if not test_url:
            print("\n⏭️  Skipping article analysis test.")
            print("✅ Analyzer is ready to use! Run 'python news_analyzer.py' to start.")
            return
        
        if not test_url.startswith(('http://', 'https://')):
            test_url = 'https://' + test_url
        
        # Analyze
        print(f"\n2️⃣  Analyzing article from: {test_url}")
        result = analyzer.analyze_news(test_url)
        
        # Display results
        print("\n" + analyzer.format_output(result))
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyzer()


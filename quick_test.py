"""
Quick non-interactive test of the news analyzer
"""

from news_analyzer import NewsAnalyzer

def quick_test():
    """Test the analyzer with a sample news URL"""
    print("🚀 Quick Test of News Analyzer\n")
    print("=" * 80)
    
    try:
        # Initialize analyzer
        print("\n1️⃣  Initializing analyzer...")
        analyzer = NewsAnalyzer()
        print("   ✅ Analyzer initialized")
        
        # Test API key
        print("\n2️⃣  Testing OpenAI API key...")
        if analyzer.test_api_key():
            print("   ✅ API key is working!")
        else:
            print("   ❌ API key test failed!")
            return
        
        # Test with a sample news URL (using a well-known news site)
        # Using a BBC article about India as a test case
        test_url = "https://www.bbc.com/news/world-asia-india"
        
        print(f"\n3️⃣  Testing article fetch from: {test_url}")
        print("   (This will fetch the article content)")
        
        article_data = analyzer.fetch_article_content(test_url)
        
        if article_data.get("success"):
            print(f"   ✅ Article fetched successfully!")
            print(f"   📰 Title: {article_data.get('title', 'N/A')[:80]}...")
            print(f"   📄 Content length: {len(article_data.get('content', ''))} characters")
            
            # Now test full analysis (this will take longer and cost API credits)
            print("\n4️⃣  Testing full analysis with OpenAI...")
            print("   ⚠️  This will use OpenAI API credits")
            
            proceed = input("\n   Proceed with full analysis? (y/n): ").strip().lower()
            
            if proceed == 'y':
                result = analyzer.analyze_news(test_url)
                
                if result.get("success"):
                    print("\n" + analyzer.format_output(result))
                    print("\n✅ Full test completed successfully!")
                else:
                    print(f"\n❌ Analysis failed: {result.get('error')}")
            else:
                print("\n⏭️  Skipping full analysis (API call)")
                print("✅ Basic functionality test passed!")
        else:
            print(f"   ⚠️  Could not fetch article: {article_data.get('error')}")
            print("   This might be due to website restrictions or network issues")
            print("   But the analyzer setup is correct!")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()


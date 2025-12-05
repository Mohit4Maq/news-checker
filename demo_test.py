"""
Demo test with a sample article to show full analysis capabilities
"""

from news_analyzer import NewsAnalyzer
import json

def demo_test():
    """Test the analyzer with a sample article"""
    print("🚀 Demo Test of News Analyzer\n")
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
        
        # Create a sample article for testing
        print("\n3️⃣  Creating sample article for analysis...")
        sample_article = {
            "success": True,
            "title": "Government Announces New Economic Policy Affecting Millions of Indians",
            "content": """
            In a major announcement today, the government revealed a new economic policy that will 
            directly impact over 500 million citizens across India. The policy, which was approved 
            by the cabinet yesterday, promises to create 10 million new jobs in the next two years.
            
            According to sources close to the government, this policy has been in development for 
            over a year and has received support from major economic experts. However, opposition 
            leaders have raised concerns about the implementation timeline and potential impact on 
            existing industries.
            
            The policy includes several key components:
            - Tax incentives for small businesses
            - Infrastructure development in rural areas
            - Digital transformation initiatives
            - Skill development programs
            
            Critics argue that similar promises were made in the past but not fulfilled. Supporters 
            claim this time is different because of new funding mechanisms and international support.
            
            The announcement comes at a critical time when unemployment rates have been rising, 
            and economic growth has slowed. Experts are divided on whether this policy will be 
            effective, with some calling it a game-changer and others dismissing it as political 
            rhetoric.
            
            No official government spokesperson was available for comment at the time of publication.
            """,
            "url": "https://example-news-site.com/sample-article"
        }
        
        print("   ✅ Sample article created")
        print(f"   📰 Title: {sample_article['title']}")
        
        # Load rules
        print("\n4️⃣  Loading analysis rules...")
        rules = analyzer.load_rules()
        if rules:
            print(f"   ✅ Rules loaded ({len(rules)} characters)")
        else:
            print("   ⚠️  Rules file not found, but continuing...")
        
        # Create analysis prompt
        print("\n5️⃣  Creating analysis prompt...")
        prompt = analyzer.create_analysis_prompt(sample_article, rules)
        print(f"   ✅ Prompt created ({len(prompt)} characters)")
        
        # Run full analysis
        print("\n6️⃣  Running full analysis with OpenAI GPT-4o...")
        print("   ⏳ This may take 30-60 seconds...")
        
        # For demo, we'll manually call the API with our sample article
        try:
            response = analyzer.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert news analyst and fact-checker specializing in Indian news. You provide detailed, objective analysis based on comprehensive rules and guidelines."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            analysis_text = response.choices[0].message.content
            print("   ✅ Analysis received from OpenAI")
            
            # Try to parse JSON
            try:
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    analysis_text = analysis_text[json_start:json_end].strip()
                elif "```" in analysis_text:
                    json_start = analysis_text.find("```") + 3
                    json_end = analysis_text.find("```", json_start)
                    analysis_text = analysis_text[json_start:json_end].strip()
                
                analysis_json = json.loads(analysis_text)
                
                # Create result object
                result = {
                    "success": True,
                    "url": sample_article["url"],
                    "article": sample_article,
                    "analysis": analysis_json
                }
                
                # Display formatted output
                print("\n" + "=" * 80)
                print(analyzer.format_output(result))
                print("\n✅ Demo test completed successfully!")
                
            except json.JSONDecodeError:
                print("\n⚠️  Could not parse JSON response, showing raw output:")
                print("\n" + "=" * 80)
                print(analysis_text[:2000])  # Show first 2000 chars
                print("\n✅ Analysis received (JSON parsing issue, but API call worked)")
        
        except Exception as e:
            print(f"\n❌ OpenAI API error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_test()


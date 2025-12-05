# News Checker - Fact-Checking & Propaganda Detection System

A comprehensive news analysis tool that uses OpenAI's GPT-4 to analyze news articles, detect propaganda, verify facts, and assess relevance to India.

## Features

- 🔍 **Fact-Checking**: Verifies claims and checks for factual accuracy
- 🚨 **Propaganda Detection**: Identifies emotional manipulation, bias, and agenda-driven content
- 🇮🇳 **India-Specific Analysis**: Assesses relevance and impact on Indian citizens
- 📊 **Comprehensive Scoring**: Multi-dimensional analysis with detailed scoring
- 📋 **Detailed Reports**: Provides comprehensive verdicts with reasoning

## Setup

1. **Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - Ensure your `.env` file contains:
     ```
     OPEN_AI_API="your-api-key-here"
     ```

## Usage

### Web UI (Recommended)

Launch the Streamlit web interface:
```bash
source venv/bin/activate
streamlit run app.py
```

The UI will open in your browser automatically. Simply paste a news URL and click "Analyze News"!

### Interactive Mode (Command Line)

Run the analyzer:
```bash
source venv/bin/activate
python news_analyzer.py
```

Then enter a news URL when prompted.

### Programmatic Usage

```python
from news_analyzer import NewsAnalyzer

# Initialize analyzer
analyzer = NewsAnalyzer()

# Test API key
if analyzer.test_api_key():
    print("API key is working!")

# Analyze a news article
result = analyzer.analyze_news("https://example.com/news-article")

# Format and display results
print(analyzer.format_output(result))
```

## Analysis Framework

The system analyzes news articles based on:

1. **Factual Accuracy (0-30 points)**: Verification of claims and sources
2. **Source Credibility (0-20 points)**: Assessment of source reliability
3. **Bias Level (0-15 points)**: Detection of political, commercial, or other biases
4. **Propaganda Indicators (0-15 points)**: Emotional manipulation, logical fallacies
5. **India Relevance (0-20 points)**: Impact on India and Indian citizens

**Total Score: 0-100 points**

### Categories

- **FACTUAL NEWS**: Verified, credible, balanced reporting
- **PROPAGANDA**: Agenda-driven, manipulative content
- **MISINFORMATION**: False or unverified information
- **OPINION/ANALYSIS**: Clearly labeled opinion pieces
- **SATIRE/PARODY**: Humorous or satirical content

## Rules Document

The analysis is based on comprehensive rules defined in `NEWS_ANALYSIS_RULES.md`, which includes:

- Core definitions of factual news vs propaganda
- Detailed propaganda indicators
- Fact-checking guidelines
- India-specific relevance framework
- Bias detection criteria
- Source credibility assessment

## Example Output

```
📰 NEWS ANALYSIS REPORT
================================================================================
🔗 URL: https://example.com/news
📌 Title: Example News Article

🎯 OVERALL VERDICT: PROPAGANDA
📊 Overall Score: 35/100

📈 DETAILED SCORING:
--------------------------------------------------------------------------------
✅ Factual Accuracy: 8/30
   Multiple unverified claims found...

📚 Source Credibility: 5/20
   Relies on anonymous sources...

🇮🇳 India Relevance: 15/20
   High relevance to Indian policy...
```

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for fetching articles

## License

This project is for educational and research purposes.


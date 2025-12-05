# 📰 News Checker - AI-Powered Fact-Checking & Propaganda Detection

A comprehensive news analysis tool that uses OpenAI's GPT models to analyze news articles, detect propaganda, verify facts, assess bias, identify beneficiaries, and provide world-class reporting comparisons - specifically designed for Indian news media.

## 🌟 Key Features

- 🔍 **Comprehensive Fact-Checking**: Multi-dimensional analysis with detailed scoring
- 🚨 **Propaganda Detection**: Identifies emotional manipulation, bias, and agenda-driven content
- 💰 **Beneficiary Analysis**: Identifies who benefits, hidden agendas, and connections
- 🌍 **World-Class Comparison**: Compares articles against BBC, Reuters, Guardian, NYT standards with visual graphs
- 👥 **Citizen Accountability**: Identifies what questions should be asked and what's missing
- 📰 **True Report Generation**: Creates complete, unbiased reports showing how news should be reported
- 🔗 **Related Articles Analysis**: Compares with other articles on the same website
- 🇮🇳 **India-Specific Analysis**: Assesses relevance and impact on Indian citizens
- 📊 **Interactive Visualizations**: Charts and graphs comparing reporting quality
- 🎯 **Critical Opposition Reporter**: Analyzes news from citizen's perspective, questioning everything

## 🚀 Live Demo

**Try it now**: [Deploy on Streamlit Cloud](#streamlit-cloud-deployment)

## 📋 Analysis Framework

The system provides comprehensive analysis across multiple dimensions:

### Scoring System (0-100 points)
1. **Factual Accuracy (0-30 points)**: Verification of claims and sources
2. **Source Credibility (0-20 points)**: Assessment of source reliability
3. **Bias Level (0-15 points)**: Detection of political, commercial, or other biases
4. **Propaganda Indicators (0-15 points)**: Emotional manipulation, logical fallacies
5. **India Relevance (0-20 points)**: Impact on India and Indian citizens

### Analysis Categories
- **FACTUAL NEWS**: Verified, credible, balanced reporting
- **PROPAGANDA**: Agenda-driven, manipulative content
- **MISINFORMATION**: False or unverified information
- **OPINION/ANALYSIS**: Clearly labeled opinion pieces
- **SATIRE/PARODY**: Humorous or satirical content

### Special Features
- **Beneficiary Analysis**: Who benefits, connections, hidden agendas
- **World-Class Comparison**: Visual comparison with BBC, Reuters, Guardian, NYT
- **True Report**: Complete unbiased report showing how it should be written
- **Citizen Accountability**: What questions should be asked, what's missing
- **Related Articles**: Comparison with other articles on same website

## 🛠️ Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Mohit4Maq/news-checker.git
   cd news-checker
   ```

2. **Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   Create a `.env` file in the root directory:
   ```
   OPEN_AI_API=your-openai-api-key-here
   ```

4. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 🚀 Streamlit Cloud Deployment

### Quick Deploy (5 minutes)

1. **Fork or use this repository**: https://github.com/Mohit4Maq/news-checker

2. **Go to Streamlit Cloud**: https://share.streamlit.io/

3. **Sign in** with your GitHub account

4. **Click "New app"**

5. **Configure your app**:
   - **Repository**: `your-username/news-checker` (or `Mohit4Maq/news-checker`)
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain

6. **Add Secrets** (Environment Variables):
   - Click "Advanced settings" → "Secrets"
   - Add:
     ```toml
     OPEN_AI_API = "your-openai-api-key-here"
     ```

7. **Click "Deploy"**

8. **Your app will be live at**: `https://your-app-name.streamlit.app`

### Updating the Deployed App

Simply push changes to the `main` branch:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Streamlit Cloud will automatically redeploy!

## 📖 Usage

### Web UI (Recommended)

1. Launch the Streamlit app (see Setup above)
2. Enter a news article URL or paste article content
3. Click "Analyze News"
4. View comprehensive analysis with visualizations

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

## 📚 Documentation

- **QUICKSTART.md**: Quick setup guide
- **NEWS_ANALYSIS_RULES.md**: Comprehensive analysis rules and framework
- **DEPLOYMENT.md**: Detailed deployment instructions
- **ADVANCED_FETCHING.md**: Advanced article fetching methods
- **WORKAROUNDS_SUMMARY.md**: Solutions for blocked websites

## 🔧 Requirements

- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com/)
- Internet connection for fetching articles

## 📝 Example Output

The system provides:
- Overall verdict and score
- Detailed category-by-category analysis
- Beneficiary and hidden agenda analysis
- World-class reporting comparison with visual charts
- Citizen accountability questions
- True Report (how it should have been written)
- Related articles comparison

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Important Notes

- **API Costs**: This tool uses OpenAI's API, which incurs costs. Monitor your usage.
- **Rate Limits**: Be aware of OpenAI's rate limits when analyzing multiple articles.
- **Privacy**: Article content is sent to OpenAI for analysis. Don't use with sensitive/confidential content.

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Built with OpenAI's GPT models
- UI powered by Streamlit
- Visualizations using Plotly

---

**Made with ❤️ for transparent journalism and informed citizens**

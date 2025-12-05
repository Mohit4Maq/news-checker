# Quick Start Guide - News Checker UI

## 🚀 Running the Web UI

### Option 1: Using the run script (Easiest)
```bash
./run_ui.sh
```

### Option 2: Manual start
```bash
source venv/bin/activate
streamlit run app.py
```

### Option 3: Direct command
```bash
cd /Users/mohitchand/Cursor_tryouts/news_check
source venv/bin/activate
streamlit run app.py
```

## 📱 What to Expect

1. **Terminal Output**: You'll see something like:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Browser**: Streamlit will automatically open your default browser to the app

3. **If browser doesn't open**: Copy the Local URL from terminal and paste in your browser

## 🎯 Using the UI

1. **Enter URL**: Paste a news article URL in the input field
2. **Click "Analyze News"**: Wait 30-60 seconds for analysis
3. **View Results**: See detailed scores, verdict, and India-specific analysis
4. **Review Findings**: Check key findings and recommendations

## ✨ Features

- ✅ Clean, modern interface
- 📊 Visual score breakdowns
- 🇮🇳 India-specific analysis
- 🎨 Color-coded verdicts
- 📋 Detailed explanations

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where Streamlit is running.

## 🔧 Troubleshooting

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Can't find analyzer?**
- Make sure `.env` file exists with `OPEN_AI_API` key
- Check that virtual environment is activated

**Import errors?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```


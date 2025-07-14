# 🧠 Reddit Persona Analyzer — Backend

This is the backend server for the **Reddit Persona Analyzer** — a tool that generates a detailed psychological and behavioral profile of any public Reddit user, based on their posts and comments.

The backend uses:
- 🧠 `PRAW` for Reddit API interaction  
- 📊 `NLTK` and `TextBlob` for sentiment and topic analysis  
- ⚙️ `Flask` for serving the API  
- 🔐 Environment variables for API credentials

---

## 🚀 Features

- Fetches public Reddit posts/comments for any user
- Extracts sentiment, subreddit activity, and topic interests
- Generates a `.txt` persona report including:
  - Sentiment breakdown
  - Subreddit engagement
  - Interests and keywords
  - Personality insights
  - Evidence and citations

---

## 📂 Project Structure

backend/
│
├── app.py # Flask API
├── reddit_persona_analyzer.py # Main analysis engine
├── requirements.txt # Dependencies
├── .env # (Optional) Local environment vars
└── output/ # Where reports are saved

## 🔐 Environment Variables (Render / .env)

| Variable               | Description                            |
|------------------------|----------------------------------------|
| `REDDIT_CLIENT_ID`     | From [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| `REDDIT_CLIENT_SECRET` | Your app’s secret key                 |
| `REDDIT_USER_AGENT`    | Custom name like `PersonaAnalyzer/1.0 by u/yourusername` |



## Install Requirements

pip install -r requirements.txt

## Run the API Server

python app.py

## Author
Arnav Gupta
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


---

## 🧾 Alternative: Run Script Directly Without Frontend

If you don't want to use the frontend or deploy it, you can run the analyzer directly from the command line.

### ▶️ Run the Script Standalone
In terminal run 
python reddit_persona_analyzer.py

## You’ll be prompted like this:

Paste Reddit profile URL (or 'exit'): https://www.reddit.com/user/kojied/

## ✅ The script will:

Extract the username

Analyze posts and comments

Generate a .txt report in the output/ folder

### Make sure your environment variables are set either via .env file or system variables:
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=PersonaAnalyzer/1.0 by u/yourusername



## Author
Arnav Gupta

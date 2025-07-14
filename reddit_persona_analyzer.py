import os
import sys
import re
import json
import praw
import argparse
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any
from dotenv import load_dotenv
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    sys.exit("Error: Reddit API credentials not found. Please set them as environment variables on Render / .env file.")

DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", 100))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
DELAY_BETWEEN_REQUESTS = int(os.getenv("DELAY_BETWEEN_REQUESTS", 1))
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "txt")
INCLUDE_CITATIONS = os.getenv("INCLUDE_CITATIONS", "True") == "True"
VERBOSE_OUTPUT = os.getenv("VERBOSE_OUTPUT", "True") == "True"

try:
    from textblob import TextBlob
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.sentiment import SentimentIntensityAnalyzer
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("vader_lexicon", quiet=True)
except ImportError:
    sys.exit("Required libraries missing. Run: pip install praw textblob nltk flask flask_cors")

class RedditUserAnalyzer:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words("english"))

    @staticmethod
    def extract_username_from_url(url: str) -> str:
        patterns = [r"reddit\.com/(?:u|user)/([^/]+)/?"]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)
        raise ValueError("Invalid Reddit profile URL")

    def _sentiment(self, text: str):
        return self.sentiment_analyzer.polarity_scores(text)

    def get_user_data(self, username: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        u = self.reddit.redditor(username)
        if u is None:
            raise ValueError("User not found")
        data = {
            "username": username,
            "account_created": datetime.fromtimestamp(u.created_utc),
            "karma_post": u.link_karma,
            "karma_comment": u.comment_karma,
            "posts": [],
            "comments": [],
        }
        for p in u.submissions.new(limit=limit):
            data["posts"].append({
                "title": p.title,
                "text": p.selftext,
                "score": p.score,
                "subreddit": p.subreddit.display_name,
                "url": f"https://reddit.com{p.permalink}",
            })
        for c in u.comments.new(limit=limit):
            data["comments"].append({
                "text": c.body,
                "score": c.score,
                "subreddit": c.subreddit.display_name,
                "url": f"https://reddit.com{c.permalink}",
            })
        return data

    def save_persona_to_txt(self, user_data: Dict[str, Any], filename: str):
        texts = [f"{p['title']} {p['text']}" for p in user_data['posts']] + [c['text'] for c in user_data['comments']]
        s = [self._sentiment(t) for t in texts if t.strip()]
        avg = {k: sum(x[k] for x in s) / len(s) if s else 0 for k in ("compound", "pos", "neg", "neu")}

        sub_counts = defaultdict(int)
        for p in user_data['posts']:
            sub_counts[p['subreddit']] += 1
        for c in user_data['comments']:
            sub_counts[c['subreddit']] += 1

        top_subs = sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calculate interests (simple word frequency)
        combined_text = ' '.join(texts).lower()
        tokens = word_tokenize(combined_text)
        keywords = [t for t in tokens if t.isalnum() and t not in self.stop_words and len(t) > 2]
        word_freq = Counter(keywords)
        interest_categories = {
            'technology': ['python', 'programming', 'software', 'tech', 'computer', 'code', 'development', 'ai', 'machine', 'learning'],
            'gaming': ['game', 'gaming', 'play', 'player', 'steam', 'console', 'xbox', 'playstation', 'nintendo', 'fps', 'rpg'],
            'finance': ['money', 'investment', 'stock', 'crypto', 'bitcoin', 'trading', 'portfolio', 'financial', 'market'],
            'fitness': ['gym', 'workout', 'exercise', 'fitness', 'muscle', 'weight', 'training', 'health', 'diet'],
            'entertainment': ['movie', 'film', 'tv', 'show', 'series', 'music', 'band', 'song', 'album', 'netflix'],
            'sports': ['football', 'basketball', 'soccer', 'baseball', 'sport', 'team', 'game', 'match', 'player', 'season'],
            'politics': ['government', 'political', 'politics', 'election', 'vote', 'politician', 'policy', 'law', 'congress'],
            'education': ['school', 'university', 'college', 'student', 'study', 'education', 'learn', 'teacher', 'class', 'degree']
        }
        interests = {}
        for cat, words in interest_categories.items():
            score = sum(word_freq.get(w, 0) for w in words)
            if score > 0:
                interests[cat] = score
        top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:5]

        # Personality Insights
        insights = {}
        if avg['compound'] > 0.3:
            insights['mood'] = "Generally positive and optimistic"
        elif avg['compound'] < -0.3:
            insights['mood'] = "Tends to be critical or negative"
        else:
            insights['mood'] = "Balanced emotional expression"
        if len(user_data['comments']) > 3 * len(user_data['posts']):
            insights['engagement'] = "Highly interactive, prefers commenting over posting"
        elif len(user_data['posts']) > len(user_data['comments']):
            insights['engagement'] = "Content creator, prefers sharing original posts"
        else:
            insights['engagement'] = "Balanced between posting and commenting"
        if top_interests:
            insights['primary_interest'] = f"Primarily interested in {top_interests[0][0]}"

        # Citations
        all_items = [
            {"type": "post", "text": f"{p['title']} {p['text']}", "score": p['score'], "url": p['url'], "subreddit": p['subreddit']} for p in user_data['posts']
        ] + [
            {"type": "comment", "text": c['text'], "score": c['score'], "url": c['url'], "subreddit": c['subreddit']} for c in user_data['comments']
        ]
        citations = sorted(all_items, key=lambda x: x['score'], reverse=True)[:5]
        for c in citations:
            c['text'] = c['text'][:200]

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Reddit User Persona Analysis\n" + "="*50 + "\n\n")
            f.write(f"Username: {user_data['username']}\n")
            f.write(f"Account Created: {user_data['account_created'].strftime('%Y-%m-%d')}\n")
            f.write(f"Post Karma: {user_data['karma_post']}\n")
            f.write(f"Comment Karma: {user_data['karma_comment']}\n\n")

            f.write("Activity Summary:\n")
            f.write(f"- Total Posts: {len(user_data['posts'])}\n")
            f.write(f"- Total Comments: {len(user_data['comments'])}\n")
            f.write(f"- Average Post Score: {avg['pos']*100:.2f}\n")
            f.write(f"- Average Comment Score: {avg['neu']*100:.2f}\n\n")

            f.write("Sentiment Analysis:\n")
            f.write(f"- Overall Sentiment: {avg['compound']:.3f}\n")
            f.write(f"- Positive: {avg['pos']:.3f}\n")
            f.write(f"- Negative: {avg['neg']:.3f}\n")
            f.write(f"- Neutral: {avg['neu']:.3f}\n\n")

            f.write("Top Interests:\n")
            for i, (topic, score) in enumerate(top_interests):
                f.write(f"- {topic.title()}: {score}\n")
            f.write("\n")

            f.write("Most Active Subreddits:\n")
            for sub, count in top_subs:
                f.write(f"- r/{sub}: {count} posts/comments\n")
            f.write("\n")

            f.write("Personality Insights:\n")
            for k, v in insights.items():
                f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
            f.write("\n")

            f.write("Citations and Evidence:\n")
            for i, c in enumerate(citations, 1):
                f.write(f"{i}. {c['type'].title()} in r/{c['subreddit']} (Score: {c['score']})\n")
                f.write(f"   Content: {c['text']}\n")
                f.write(f"   Source: {c['url']}\n\n")

            f.write("Analysis completed on: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print("Persona saved to:", filename)

def main():
    ana = RedditUserAnalyzer()
    while True:
        url = input("\nPaste Reddit profile URL (or 'exit'): ").strip()
        if url.lower() == "exit":
            break
        try:
            user = ana.extract_username_from_url(url)
            data = ana.get_user_data(user)
            out = f"output/{user}_persona.txt"
            os.makedirs("output", exist_ok=True)
            ana.save_persona_to_txt(data, out)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()

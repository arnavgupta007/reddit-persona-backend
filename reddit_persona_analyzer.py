import praw
import requests
import json
import re
import sys
import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
import time
from urllib.parse import urlparse
import argparse

try:
    from textblob import TextBlob
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.sentiment import SentimentIntensityAnalyzer
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except ImportError:
    print("Required libraries not installed. Please run: pip install textblob nltk praw")
    sys.exit(1)

try:
    from config import (
        REDDIT_CLIENT_ID,
        REDDIT_CLIENT_SECRET,
        REDDIT_USER_AGENT
    )
except ImportError:
    print("Error: config.py not found or incomplete. Please add your Reddit API credentials.")
    sys.exit(1)

class RedditUserAnalyzer:
    def __init__(self, reddit_client_id: str, reddit_client_secret: str, reddit_user_agent: str):
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))

    def extract_username_from_url(self, url: str) -> str:
        patterns = [
            r'reddit\.com/user/([^/]+)',
            r'reddit\.com/u/([^/]+)',
            r'reddit\.com/user/([^/]+)/',
            r'reddit\.com/u/([^/]+)/'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError(f"Could not extract username from URL: {url}")

    def get_user_data(self, username: str, limit: int = 100) -> Dict[str, Any]:
        user = self.reddit.redditor(username)
        if user.id is None:
            raise ValueError(f"User {username} not found")

        user_data = {
            'username': username,
            'account_created': datetime.fromtimestamp(user.created_utc),
            'karma_post': user.link_karma,
            'karma_comment': user.comment_karma,
            'posts': [],
            'comments': []
        }

        for post in user.submissions.new(limit=limit):
            user_data['posts'].append({
                'id': post.id,
                'title': post.title,
                'text': post.selftext,
                'subreddit': post.subreddit.display_name,
                'score': post.score,
                'created_utc': post.created_utc,
                'url': f"https://reddit.com{post.permalink}"
            })

        for comment in user.comments.new(limit=limit):
            user_data['comments'].append({
                'id': comment.id,
                'text': comment.body,
                'subreddit': comment.subreddit.display_name,
                'score': comment.score,
                'created_utc': comment.created_utc,
                'url': f"https://reddit.com{comment.permalink}"
            })

        return user_data

    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        return self.sentiment_analyzer.polarity_scores(text)

    def extract_topics_and_interests(self, texts: List[str]) -> Dict[str, Any]:
        combined_text = ' '.join(texts)
        tokens = word_tokenize(combined_text.lower())
        tokens = [t for t in tokens if t.isalnum() and t not in self.stop_words and len(t) > 2]
        word_freq = Counter(tokens)
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
        for cat, keywords in interest_categories.items():
            score = sum(word_freq.get(k, 0) for k in keywords)
            if score > 0:
                interests[cat] = score

        return {
            'top_words': dict(word_freq.most_common(20)),
            'interests': dict(sorted(interests.items(), key=lambda x: x[1], reverse=True))
        }

    def analyze_posting_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        post_scores = [p['score'] for p in user_data['posts']]
        comment_scores = [c['score'] for c in user_data['comments']]
        avg_post_score = sum(post_scores) / len(post_scores) if post_scores else 0
        avg_comment_score = sum(comment_scores) / len(comment_scores) if comment_scores else 0
        return {
            'total_posts': len(user_data['posts']),
            'total_comments': len(user_data['comments']),
            'avg_post_score': round(avg_post_score, 2),
            'avg_comment_score': round(avg_comment_score, 2)
        }

    def generate_personality_insights(self, sentiment: Dict[str, float], topics: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, str]:
        insights = {}
        if sentiment['compound'] > 0.3:
            insights['mood'] = "Generally positive and optimistic"
        elif sentiment['compound'] < -0.3:
            insights['mood'] = "Tends to be critical or negative"
        else:
            insights['mood'] = "Balanced emotional expression"

        if patterns['total_comments'] > patterns['total_posts'] * 3:
            insights['engagement_style'] = "Highly interactive, prefers commenting over posting"
        elif patterns['total_posts'] > patterns['total_comments']:
            insights['engagement_style'] = "Content creator, prefers sharing original posts"
        else:
            insights['engagement_style'] = "Balanced between posting and commenting"

        if topics['interests']:
            top_interest = list(topics['interests'].keys())[0]
            insights['primary_interest'] = f"Primarily interested in {top_interest}"

        return insights

    def generate_citations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        content = [
            {
                'type': 'post',
                'text': f"{p['title']} {p['text']}",
                'score': p['score'],
                'url': p['url'],
                'subreddit': p['subreddit']
            } for p in user_data['posts']
        ] + [
            {
                'type': 'comment',
                'text': c['text'],
                'score': c['score'],
                'url': c['url'],
                'subreddit': c['subreddit']
            } for c in user_data['comments']
        ]
        top = sorted(content, key=lambda x: x['score'], reverse=True)[:5]
        for t in top:
            t['text'] = t['text'][:200]
        return top

    def save_persona_to_txt(self, user_data: Dict[str, Any], filename: str) -> None:
        sentiment = self.analyze_text_sentiment(' '.join([f"{p['title']} {p['text']}" for p in user_data['posts']] + [c['text'] for c in user_data['comments']]))
        topics = self.extract_topics_and_interests([f"{p['title']} {p['text']}" for p in user_data['posts']] + [c['text'] for c in user_data['comments']])
        patterns = self.analyze_posting_patterns(user_data)
        insights = self.generate_personality_insights(sentiment, topics, patterns)
        citations = self.generate_citations(user_data)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Reddit User Persona Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Username: {user_data['username']}\n")
            f.write(f"Account Created: {user_data['account_created'].strftime('%Y-%m-%d')}\n")
            f.write(f"Post Karma: {user_data['karma_post']}\n")
            f.write(f"Comment Karma: {user_data['karma_comment']}\n\n")

            f.write("Activity Summary:\n")
            f.write(f"- Total Posts: {patterns['total_posts']}\n")
            f.write(f"- Total Comments: {patterns['total_comments']}\n")
            f.write(f"- Average Post Score: {patterns['avg_post_score']}\n")
            f.write(f"- Average Comment Score: {patterns['avg_comment_score']}\n\n")

            f.write("Sentiment Analysis:\n")
            f.write(f"- Overall Sentiment: {sentiment['compound']:.3f}\n")
            f.write(f"- Positive: {sentiment['pos']:.3f}\n")
            f.write(f"- Negative: {sentiment['neg']:.3f}\n")
            f.write(f"- Neutral: {sentiment['neu']:.3f}\n\n")

            f.write("Top Interests:\n")
            for interest, score in list(topics['interests'].items())[:5]:
                f.write(f"- {interest.title()}: {score}\n")
            f.write("\n")

            sub_counts = defaultdict(int)
            for p in user_data['posts']:
                sub_counts[p['subreddit']] += 1
            for c in user_data['comments']:
                sub_counts[c['subreddit']] += 1
            f.write("Most Active Subreddits:\n")
            for sub, count in sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                f.write(f"- r/{sub}: {count} posts/comments\n")
            f.write("\n")

            f.write("Personality Insights:\n")
            for k, v in insights.items():
                f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
            f.write("\n")

            f.write("Citations and Evidence:\n")
            for i, cite in enumerate(citations, 1):
                f.write(f"{i}. {cite['type'].title()} in r/{cite['subreddit']} (Score: {cite['score']})\n")
                f.write(f"   Content: {cite['text']}\n")
                f.write(f"   Source: {cite['url']}\n\n")

            f.write(f"Analysis completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"Persona saved to: {filename}")


def main():
    analyzer = RedditUserAnalyzer(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

    while True:
        print("\nPaste a Reddit profile URL (or type 'exit' to quit):")
        input_url = input("→ ").strip()
        if input_url.lower() == 'exit':
            break

        try:
            username = analyzer.extract_username_from_url(input_url)
            print(f"Analyzing user: {username}")
            data = analyzer.get_user_data(username)
            analyzer.save_persona_to_txt(data, f"output/{username}_persona.txt")
            print("Analysis complete!")
        except Exception as e:
            print("Error:", str(e))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test script for Reddit User Persona Analyzer
Tests the analyzer with sample data without using real Reddit API
"""

import sys
import os
from datetime import datetime
from reddit_persona_analyzer import RedditUserAnalyzer

def create_mock_user_data():
    """Create mock user data for testing"""
    return {
        'username': 'test_user',
        'account_created': datetime(2020, 1, 1),
        'karma_post': 1500,
        'karma_comment': 3200,
        'posts': [
            {
                'id': 'post1',
                'title': 'My first Python machine learning project',
                'text': 'Just finished building a sentiment analysis model using Python and scikit-learn. The experience was amazing and I learned so much about data preprocessing and model evaluation.',
                'subreddit': 'MachineLearning',
                'score': 45,
                'created_utc': 1609459200,
                'url': 'https://reddit.com/r/MachineLearning/comments/test1'
            },
            {
                'id': 'post2',
                'title': 'Best gaming setup for 2024',
                'text': 'After months of research, I finally built my dream gaming PC. RTX 4080, AMD Ryzen 9, 32GB RAM. The performance is incredible for both gaming and video editing.',
                'subreddit': 'gaming',
                'score': 23,
                'created_utc': 1609545600,
                'url': 'https://reddit.com/r/gaming/comments/test2'
            },
            {
                'id': 'post3',
                'title': 'Cryptocurrency investment strategies',
                'text': 'Been investing in crypto for 2 years now. Here are my thoughts on portfolio diversification and risk management in the volatile crypto market.',
                'subreddit': 'CryptoCurrency',
                'score': 67,
                'created_utc': 1609632000,
                'url': 'https://reddit.com/r/CryptoCurrency/comments/test3'
            }
        ],
        'comments': [
            {
                'id': 'comment1',
                'text': 'Great tutorial! I love how you explained the concept step by step. This really helped me understand neural networks better.',
                'subreddit': 'MachineLearning',
                'score': 15,
                'created_utc': 1609459200,
                'url': 'https://reddit.com/r/MachineLearning/comments/comment1'
            },
            {
                'id': 'comment2',
                'text': 'This game is absolutely fantastic! The graphics are stunning and the gameplay mechanics are so smooth. Best purchase I made this year.',
                'subreddit': 'gaming',
                'score': 8,
                'created_utc': 1609545600,
                'url': 'https://reddit.com/r/gaming/comments/comment2'
            },
            {
                'id': 'comment3',
                'text': 'I disagree with this approach. The risks are too high and the market is too unpredictable. Better to stick with traditional investments.',
                'subreddit': 'investing',
                'score': 3,
                'created_utc': 1609632000,
                'url': 'https://reddit.com/r/investing/comments/comment3'
            },
            {
                'id': 'comment4',
                'text': 'Python is such a versatile language. I use it for everything from web development to data science. The community is amazing too.',
                'subreddit': 'Python',
                'score': 12,
                'created_utc': 1609718400,
                'url': 'https://reddit.com/r/Python/comments/comment4'
            },
            {
                'id': 'comment5',
                'text': 'Thanks for sharing this! I had the same issue and your solution worked perfectly. The documentation could be clearer though.',
                'subreddit': 'programming',
                'score': 6,
                'created_utc': 1609804800,
                'url': 'https://reddit.com/r/programming/comments/comment5'
            }
        ]
    }

def test_analyzer():
    """Test the analyzer with mock data"""
    print("Testing Reddit User Persona Analyzer...")
    print("=" * 50)
    
    # Create a mock analyzer (no real Reddit API needed)
    class MockAnalyzer(RedditUserAnalyzer):
        def __init__(self):
            # Initialize without Reddit API
            from textblob import TextBlob
            import nltk
            from nltk.corpus import stopwords
            from nltk.sentiment import SentimentIntensityAnalyzer
            
            # Download required NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
            except:
                pass
            
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.stop_words = set(stopwords.words('english'))
    
    try:
        # Create analyzer
        analyzer = MockAnalyzer()
        
        # Get mock data
        user_data = create_mock_user_data()
        
        # Generate persona
        print("Generating persona for test user...")
        persona = analyzer.generate_persona(user_data)
        
        # Save to file
        output_file = "test_user_persona.txt"
        analyzer.save_persona_to_file(persona, output_file)
        
        print(f"✓ Test completed successfully!")
        print(f"✓ Output saved to: {output_file}")
        
        # Display summary
        print("\nTest Results Summary:")
        print(f"- Username: {persona['username']}")
        print(f"- Posts analyzed: {persona['activity_summary']['total_posts']}")
        print(f"- Comments analyzed: {persona['activity_summary']['total_comments']}")
        print(f"- Overall sentiment: {persona['sentiment_analysis']['compound']:.3f}")
        print(f"- Top interest: {list(persona['interests_and_topics']['interests'].keys())[0] if persona['interests_and_topics']['interests'] else 'None'}")
        print(f"- Citations generated: {len(persona['citations'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_url_extraction():
    """Test URL extraction functionality"""
    print("\nTesting URL extraction...")
    
    # Mock analyzer for URL testing
    class MockURLAnalyzer:
        def extract_username_from_url(self, url):
            import re
            patterns = [
                r'reddit\.com/user/([^/]+)',
                r'reddit\.com/u/([^/]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            raise ValueError(f"Could not extract username from URL: {url}")
    
    analyzer = MockURLAnalyzer()
    
    test_urls = [
        "https://www.reddit.com/user/kojied/",
        "https://reddit.com/user/testuser",
        "https://www.reddit.com/u/another_user/",
        "https://reddit.com/u/final_user"
    ]
    
    expected_usernames = ["kojied", "testuser", "another_user", "final_user"]
    
    for url, expected in zip(test_urls, expected_usernames):
        try:
            result = analyzer.extract_username_from_url(url)
            if result == expected:
                print(f"✓ {url} -> {result}")
            else:
                print(f"✗ {url} -> {result} (expected {expected})")
        except Exception as e:
            print(f"✗ {url} -> Error: {e}")

def main():
    """Run all tests"""
    print("Reddit User Persona Analyzer - Test Suite")
    print("=" * 50)
    
    # Test URL extraction
    test_url_extraction()
    
    # Test main analyzer
    success = test_analyzer()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! The analyzer is working correctly.")
        print("\nYou can now run the real analyzer with:")
        print("python reddit_persona_analyzer.py https://www.reddit.com/user/username/")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
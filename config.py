# Reddit API Configuration
# Copy this file to config.py and fill in your credentials

# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = "t9PqVwcMrRLx_JffhryeVg"
REDDIT_CLIENT_SECRET = "jK7C3qCztwGpso7iL4ZTl5t-r4OX4w"
REDDIT_USER_AGENT = "PersonaAnalyzer/1.0 by u/Powerful-Finding1424"

# Analysis Settings
DEFAULT_LIMIT = 100  # Number of posts/comments to analyze
MAX_RETRIES = 3      # Maximum API retry attempts
DELAY_BETWEEN_REQUESTS = 1  # Seconds to wait between API requests

# Output Settings
OUTPUT_FORMAT = "txt"  # Output format (txt, json, csv)
INCLUDE_CITATIONS = True  # Include citations in output
VERBOSE_OUTPUT = True     # Include detailed analysis
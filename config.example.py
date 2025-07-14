# Reddit API Configuration
# Copy this file to config.py and fill in your credentials

# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = "your_client_id_here"
REDDIT_CLIENT_SECRET = "your_client_secret_here"
REDDIT_USER_AGENT = "PersonaAnalyzer/1.0 by u/yourusername"

# Analysis Settings
DEFAULT_LIMIT = 100  # Number of posts/comments to analyze
MAX_RETRIES = 3      # Maximum API retry attempts
DELAY_BETWEEN_REQUESTS = 1  # Seconds to wait between API requests

# Output Settings
OUTPUT_FORMAT = "txt"  # Output format (txt, json, csv)
INCLUDE_CITATIONS = True  # Include citations in output
VERBOSE_OUTPUT = True     # Include detailed analysis
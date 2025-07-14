# app.py
from flask import Flask, request, send_file
from flask_cors import CORS
from reddit_persona_analyzer import RedditUserAnalyzer
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

app = Flask(__name__)
CORS(app)  # Allow requests from frontend
analyzer = RedditUserAnalyzer(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    try:
        username = analyzer.extract_username_from_url(url)
        user_data = analyzer.get_user_data(username)
        filename = f"output/{username}_persona.txt"
        analyzer.save_persona_to_txt(user_data, filename)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == '__main__':
    app.run(debug=True)

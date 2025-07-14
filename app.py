# app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reddit_persona_analyzer import RedditUserAnalyzer
import os

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# Create the analyzer instance (env vars must be set)
analyzer = RedditUserAnalyzer()

@app.route('/')
def home():
    return jsonify({"message": "Reddit Persona API is running"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    try:
        username = analyzer.extract_username_from_url(url)
        user_data = analyzer.get_user_data(username)

        os.makedirs("output", exist_ok=True)
        filename = f"output/{username}_persona.txt"
        analyzer.save_persona_to_txt(user_data, filename)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

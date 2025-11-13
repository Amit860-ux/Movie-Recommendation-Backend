from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
from model import recommend_movies

app = Flask(__name__)

# CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

DB_FILE = "database.db"

# Initialize DB
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                recommended_movies TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

init_db()


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_input = data.get('user_input', '').strip()

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    try:
        # Get recommendations
        recommended = recommend_movies(user_input)

        # Save to DB as JSON string
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recommendations (user_input, recommended_movies, timestamp)
                VALUES (?, ?, ?)
            ''', (user_input, json.dumps(recommended), timestamp))
            conn.commit()

        # Return recommendations with timestamp
        return jsonify({
            'recommended_movies': recommended,
            'timestamp': timestamp
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

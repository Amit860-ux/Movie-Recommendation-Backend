import sqlite3
import json

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT id, user_input, recommended_movies, timestamp FROM recommendations")
rows = cursor.fetchall()

for row in rows:
    id, user_input, recommended_json, timestamp = row
    try:
        # Try to load as JSON
        recommended = json.loads(recommended_json)
    except (json.JSONDecodeError, TypeError):
        # Fallback: split by comma if not JSON
        recommended = recommended_json.split(', ') if recommended_json else []

    print(f"ID: {id}\nInput: {user_input}\nRecommendations: {recommended}\nTime: {timestamp}\n")

conn.close()
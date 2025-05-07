from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from googletrans import Translator
import sqlite3
import redis
import json
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
import logging
import requests
from waitress import serve
from app import app

app = Flask(__name__)
CORS(app)
translator = Translator()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite database setup
def init_db():
    with sqlite3.connect("chat_history.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME
            )
        """)
init_db()

# Redis for caching (using Redis Labs free tier)
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Rate limiting (in-memory for simplicity)
request_counts = {}
def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = datetime.now()
        window = now - timedelta(minutes=1)
        request_counts[client_ip] = [
            ts for ts in request_counts.get(client_ip, []) if ts > window
        ]
        if len(request_counts[client_ip]) >= 10:  # 10 requests per minute
            return jsonify({"error": "Rate limit exceeded"}), 429
        request_counts[client_ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
@rate_limit
def translate():
    data = request.get_json()
    user_message = data.get("user_message")
    user_id = data.get("user_id", str(uuid.uuid4()))

    # Check cache
    cache_key = f"translate:{user_message}"
    cached_response = redis_client.get(cache_key)
    if cached_response:
        bot_response = json.loads(cached_response)
        logger.info(f"Cache hit for: {user_message}")
    else:
        # Translate to Marathi
        try:
            translation = translator.translate(user_message, dest="mr")
            bot_response = translation.text
            redis_client.setex(cache_key, 3600, json.dumps(bot_response))
            logger.info(f"Cache miss for: {user_message}")
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return jsonify({"error": str(e)}), 500

    # Store in SQLite
    with sqlite3.connect("chat_history.db") as conn:
        conn.execute(
            "INSERT INTO chats (id, user_id, user_message, bot_response, timestamp) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, user_message, bot_response, datetime.now())
        )
        conn.commit()

    # Log to external service (e.g., Logtail)
    logtail_url = os.getenv("LOGTAIL_URL")
    if logtail_url:
        requests.post(logtail_url, json={
            "message": f"User: {user_message}, Bot: {bot_response}",
            "level": "info"
        })

    return jsonify({"bot_response": bot_response})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Use the environment variable for the port
    serve(app, host="0.0.0.0", port=port)
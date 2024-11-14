from flask import Flask, request, jsonify
import os
import json
import hashlib
import psutil
from cryptography.fernet import Fernet
import sqlite3
import time
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load encryption key from environment variable
#encryption_key = os.getenv("EMAIL_ENCRYPTION_KEY")
encryption_key = b'Uo9FH4mquLYFliOCMOxenyEP51Q0XKuFzA6S7mc7EiA='
cipher = Fernet(encryption_key)

# Database setup (add this outside routes if not done already)
conn = sqlite3.connect('data/all.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        uuid TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        profile_url TEXT,
        description TEXT
    );
""")
conn.commit()
conn.close()

# Check for the existence of a "data" folder; if it doesn't exist, create it.
if not os.path.exists("data"):
    os.makedirs("data")

# Check for the existence of the "index.json" file. If it doesn't exist, create it with an empty array.
if not os.path.exists("index.json"):
    with open("index.json", "w") as f:
        f.write("{}")  # Initialize as an empty dictionary

# Optionally load the data from "index.json" if you need it for further use
with open("index.json") as data:
    index_data = json.load(data)  # Load JSON content into a variable if needed

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)


@app.route("/")
def index():
    return 'welp nothing to see here'

@app.route("/usercount")
@limiter.limit("10 per minute")
def usercount():
    # Load current count from index.json
    with open("index.json", "r") as f:
        index_data = json.load(f)
    
    # Check if "user_count" exists; if not, initialize it
    if "user_count" not in index_data:
        index_data["user_count"] = 0

    # Increment the count
    index_data["user_count"] += 1

    # Save the updated count back to index.json
    with open("index.json", "w") as f:
        json.dump(index_data, f)

    # Return the updated count as JSON
    return jsonify({"user_count": index_data["user_count"]})

@app.route('/system-stats', methods=['GET'])
def system_stats():
    # Get ping (response time) by recording time before and after a small task
    start_time = time.time()
    time.sleep(0.001)  # simulates a minimal task
    ping = (time.time() - start_time) * 1000  # Convert to milliseconds

    # RAM Usage
    ram = psutil.virtual_memory()
    ram_usage = {
        "total": ram.total,
        "available": ram.available,
        "used": ram.used,
        "free": ram.free,
        "percent": ram.percent
    }

    # CPU Usage
    cpu_usage = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(logical=True)
    }

    # Storage Stats
    disk = psutil.disk_usage('/')
    storage_stats = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent
    }

    # Combine all data into a JSON response
    stats = {
        "ping_ms": ping,
        "ram_usage": ram_usage,
        "cpu_usage": cpu_usage,
        "storage_stats": storage_stats
    }
    
    return jsonify(stats)

# login and registering with same route
@app.route("/log_reg", methods=["POST"])
def logreg():
    # Retrieve form data
    username = request.form.get("username")
    email = request.form.get("email")
    profile_url = request.form.get("profile_url")
    description = request.form.get("description")

    # Validate input
    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    if len(description) > 500:
        return jsonify({"error": "Description cannot exceed 500 characters"}), 400

    # Encrypt the email
    encrypted_email = cipher.encrypt(email.encode()).decode()

    try:
        conn = sqlite3.connect('data/all.db')
        cursor = conn.cursor()

        # Check if username and encrypted email already exist
        cursor.execute("SELECT * FROM users WHERE username = ? AND email = ?", (username, encrypted_email))
        existing_user = cursor.fetchone()

        # If the user exists, log in successfully
        if existing_user:
            decrypted_email = cipher.decrypt(existing_user[3].encode()).decode()  # Decrypt stored email for display
            return jsonify({"message": "Login successful", "user_data": {
                "id": existing_user[0],
                "username": existing_user[1],
                "uuid": existing_user[2],
                "email": decrypted_email,
                "profile_url": existing_user[4],
                "description": existing_user[5]
            }})

        # Generate a UUID and insert new user
        user_uuid = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (username, uuid, email, profile_url, description)
            VALUES (?, ?, ?, ?, ?)
        """, (username, user_uuid, encrypted_email, profile_url, description))

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully", "user_data": {
            "username": username,
            "email": email,  # Return plain email after registering
            "uuid": user_uuid,
            "profile_url": profile_url,
            "description": description
        }})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500




if __name__ == '__main__':
    app.run(debug=True,port=3456)
from flask import Flask, request, jsonify
import os
import json
import hashlib
import psutil
import sqlite3
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# connnects to database or creates it if it doesnt exists
conn = sqlite3.connect('data/all.db')
cursor = conn.cursor()
print('DB Init')


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
limiter = Limiter(app, key_func=get_remote_address)

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


if __name__ == '__main__':
    app.run(debug=True,port=3456)
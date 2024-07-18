from flask import Flask, request, jsonify
import json
import os
import psutil
import uuid
import hashlib  # Import hashlib for hashing

app = Flask(__name__)

# File to store user information
USER_FILE = 'userserverinfo.json'
# File to store secret key
KEY_FILE = 'secret.key'

# Function to ensure user file exists
def ensure_user_file_exists():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as file:
            json.dump({}, file)

# Function to generate or load secret key
def generate_or_load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    else:
        key = os.urandom(32)  # Generate a random key
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    return key

# Initialize secret key for hashing
secret_key = generate_or_load_key()

# Function to load user data from file
def load_user_data():
    ensure_user_file_exists()
    with open(USER_FILE, 'r') as file:
        return json.load(file)

# Function to save user data to file
def save_user_data(data):
    with open(USER_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Function to hash a value using SHA-256
def encrypt_value(value):
    hashed_value = hashlib.sha256(secret_key + value.encode()).hexdigest()
    return hashed_value

# Function to generate a unique user ID
def generate_user_id():
    return str(uuid.uuid4())

# Endpoint to handle user login/registration
@app.route('/user', methods=['POST'])
def user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    user_data = load_user_data()

    if username in user_data:
        if user_data[username]['email'] == email:
            decrypted_user_id = user_data[username]['user_id']
            return jsonify({"status": 231, "message": "Login successful", "user_id": decrypted_user_id})
        else:
            return jsonify({"status": 233, "message": "Invalid user credentials"})
    else:
        # Generate a unique user ID
        user_id = generate_user_id()

        # Hash the user ID
        hashed_user_id = encrypt_value(user_id)

        user_data[username] = {
            "email": email,
            "user_id": hashed_user_id  # Save hashed user ID
        }
        save_user_data(user_data)
        return jsonify({"status": 232, "message": "User registered successfully", "user_id": user_id, "secret_key": secret_key.hex()})

# Endpoint to fetch server statistics (CPU, Memory, Disk)
@app.route('/server-stats', methods=['GET'])
def server_stats():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # Get disk usage
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    # Collect stats
    stats = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage
    }

    # Return stats as JSON response
    return jsonify(stats)

# Endpoint to ping the server
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong", "status": "success"})

if __name__ == '__main__':
    app.run(debug=True,port=5000)

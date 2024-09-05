from flask import Flask, request, jsonify
import os
import json
import hashlib
import psutil

# Check if the folder 'serverdata' exists, if not, create it
if not os.path.exists('serverdata'):
    os.makedirs('serverdata')

# Check if the file 'serverdata/data.json' exists, if not, create it
if not os.path.exists('serverdata/data.json'):
    with open('serverdata/data.json', 'w') as f:
        json.dump({}, f)

app = Flask(__name__)

# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def helloworld():
    return 'Hello World!'



@app.route('/ping')
def system_stats():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Get memory usage
    memory_info = psutil.virtual_memory()
    
    # Get disk usage
    disk_info = psutil.disk_usage('/')
    
    # Get network stats
    net_info = psutil.net_io_counters()
    
    # Get boot time (system uptime)
    boot_time = psutil.boot_time()

    stats = {
        'cpu_usage': f"{cpu_usage}%",
        'memory_total': f"{memory_info.total / (1024 ** 3):.2f} GB",
        'memory_used': f"{memory_info.used / (1024 ** 3):.2f} GB",
        'memory_available': f"{memory_info.available / (1024 ** 3):.2f} GB",
        'disk_total': f"{disk_info.total / (1024 ** 3):.2f} GB",
        'disk_used': f"{disk_info.used / (1024 ** 3):.2f} GB",
        'disk_free': f"{disk_info.free / (1024 ** 3):.2f} GB",
        'bytes_sent': f"{net_info.bytes_sent / (1024 ** 2):.2f} MB",
        'bytes_received': f"{net_info.bytes_recv / (1024 ** 2):.2f} MB",
        'uptime_seconds': f"{psutil.time.time() - boot_time:.2f} seconds"
    }
    
    return jsonify(stats)

@app.route('/login', methods=['POST'])
def login():
    # Load the data from the JSON file
    with open('serverdata/data.json', 'r') as f:
        data = json.load(f)
    
    # Get username and password from the request
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username or password missing"}), 400

    hashed_password = hash_password(password)

    # Check if the user exists
    if username not in data:
        # Create a new user if it does not exist
        data[username] = {"password": hashed_password}
        with open('serverdata/data.json', 'w') as f:
            json.dump(data, f)
        return jsonify({"status": "success", "message": "User created"}), 201
    else:
        # If the user exists, check the password
        if data[username]['password'] == hashed_password:
            return jsonify({"status": "success", "message": "Login successful"}), 49
        else:
            return jsonify({"status": "error", "message": "Invalid password"}), 50

if __name__ == '__main__':
    app.run(debug=True, port="4325")

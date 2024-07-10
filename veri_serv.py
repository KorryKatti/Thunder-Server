from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

USER_FILE = 'userserverinfo.json'

# Ensure the user info file exists
def ensure_user_file_exists():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as file:
            json.dump({}, file)

# Load user data from file
def load_user_data():
    with open(USER_FILE, 'r') as file:
        return json.load(file)

# Save user data to file
def save_user_data(data):
    with open(USER_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/user', methods=['POST'])
def user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    user_id = data.get('user_id', None)  # Optional for login

    user_data = load_user_data()

    if username in user_data:
        if user_data[username]['email'] == email:
            return jsonify({"status": 231, "message": "User exists, logging in now"})
        else:
            return jsonify({"status": 233, "message": "Invalid user credentials"})
    else:
        user_data[username] = {
            "email": email,
            "user_id": user_id
        }
        save_user_data(user_data)
        return jsonify({"status": 232, "message": "User does not exist, creating a new user"})

if __name__ == '__main__':
    ensure_user_file_exists()
    app.run(debug=True)

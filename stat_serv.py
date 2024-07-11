from flask import Flask, jsonify
import psutil

app = Flask(__name__)

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

@app.route('/ping', methods=['GET'])
def ping():
    # Return a simple JSON response
    return jsonify({"message": "pong", "status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

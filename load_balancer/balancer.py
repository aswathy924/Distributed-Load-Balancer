from flask import Flask, jsonify, render_template
from algorithms import RoundRobin, LeastConnections
from health_monitor import HealthMonitor
from metrics import Metrics
import requests
import time

app = Flask(__name__)

SERVERS = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

# Start health monitor
health_monitor = HealthMonitor(SERVERS)
health_monitor.start()

USE_LEAST_CONNECTIONS = True

if USE_LEAST_CONNECTIONS:
    lb = LeastConnections([])
else:
    lb = RoundRobin([])

#  Metrics
metrics = Metrics()


@app.route("/")
def route_request():

    healthy_servers = health_monitor.get_healthy_servers()
    if isinstance(lb, LeastConnections):
        lb.update_servers(healthy_servers)
    else:
        lb.servers = healthy_servers

    server = lb.get_next_server()

    if server is None:
        return jsonify({"error": "No healthy servers available"}), 500

    start_time = time.time()

    try:
        print(f"Routing to: {server}")
        response = requests.get(server)

        duration = time.time() - start_time
        metrics.record(server, duration, success=True)

        if isinstance(lb, LeastConnections):
            lb.release_connection(server)

        return response.json()

    except Exception as e:
        duration = time.time() - start_time
        metrics.record(server, duration, success=False)

        if isinstance(lb, LeastConnections):
            lb.release_connection(server)

        return jsonify({
            "error": "Server failed",
            "details": str(e)
        }), 500


# Metrics endpoint
@app.route("/metrics")
def get_metrics():
    stats = metrics.get_stats()
    healthy_servers = health_monitor.get_healthy_servers()

    result = {}

    # Include all servers (even those with no requests yet)
    all_servers = SERVERS

    for server in all_servers:
        server_stats = stats.get(server, {
            "requests": 0,
            "failures": 0,
            "avg_response_time": 0
        })

        result[server] = {
            **server_stats,
            "status": "UP" if server in healthy_servers else "DOWN"
        }

    return jsonify(result)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    print("Load Balancer running on port 8000")
    app.run(port=8000, threaded=True)

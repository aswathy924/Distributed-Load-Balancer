from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
from algorithms import LoadBalancer
from metrics import metrics
from threading import Thread
from health_check import monitor_servers

app = Flask(__name__)
CORS(app)

VALID_ALGOS = [
    "round_robin",
    "least_connections",
    "random",
    "weighted",
    "power_of_two"
]

servers = [
    "http://backend1:5000",
    "http://backend2:5000",
    "http://backend3:5000"
]

lb = LoadBalancer(servers)
ALGO = "round_robin"
Thread(target=monitor_servers, args=(lb,), daemon=True).start()

def get_server():
    if ALGO == "round_robin":
        return lb.round_robin()
    elif ALGO == "least_connections":
        return lb.least_connections()
    elif ALGO == "random":
        return lb.random()
    elif ALGO == "weighted":
        return lb.weighted_round_robin()
    elif ALGO == "power_of_two":
        return lb.power_of_two()

@app.route("/")
def route_request():
    if not lb.servers:   
        return {"error": "No servers available"}, 500
    
    for _ in range(len(lb.servers)):

        server = get_server()

        try:
            lb.increment(server)

            start = time.time()

            response = requests.get(server, timeout=2)
            response.raise_for_status()

            response_time = time.time() - start

            lb.decrement(server)

            # NEW metrics usage
            metrics.record(server, response_time, success=True)
            metrics.set_algorithm(ALGO)

            return jsonify(response.json())

        except Exception as e:
            print(f"{server} failed: {e}")

            lb.decrement(server)

            #  record failure
            metrics.record(server, 0, success=False)

            # remove failed server
            if server in lb.servers:
                lb.servers.remove(server)

            if server in lb.connections:
                del lb.connections[server]

    return {"error": "All servers down"}, 500

@app.route("/set_algorithm/<algo>")
def set_algo(algo):
    global ALGO

    if algo not in VALID_ALGOS:
        return {"error": f"Choose from {VALID_ALGOS}"}, 400

    ALGO = algo
    return {"message": f"Algorithm set to {algo}"}

@app.route("/get_algorithm")
def get_algo():
    return {"current_algorithm": ALGO}

@app.route("/metrics")
def get_metrics():
    return jsonify(metrics.get_stats())

@app.route("/add_server", methods=["POST"])
def add_server():
    data = request.get_json()
    server = data.get("server")

    if not server:
        return {"error": "Server URL required"}, 400

    if server in lb.servers:
        return {"message": "Server already exists"}

    try:
        response = requests.get(server + "/health", timeout=2)

        if response.status_code != 200:
            return {"error": "Server not healthy"}, 400

    except:
        return {"error": "Server not reachable"}, 400

    # Only add if healthy
    lb.servers.append(server)
    lb.connections[server] = 0

    # weights update
    lb.weights[server] = 1
    lb.weighted_list = lb._build_weighted_list()

    # optional: add to metrics
    metrics.record(server, 0, success=True, is_health_check=True)

    return {"message": f"{server} added successfully"}


@app.route("/remove_server", methods=["POST"])
def remove_server():
    data = request.get_json()
    server = data.get("server")

    if not server:
        return {"error": "Server URL required"}, 400

    if server not in lb.servers:
        return {"message": "Server not found"}

    lb.servers.remove(server)
    lb.index = 0

    if server in lb.connections:
        del lb.connections[server]

    return {"message": f"{server} removed successfully"}

@app.route("/servers")
def list_servers():
    return {
        "active_servers": lb.servers,
        "connections": lb.connections
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
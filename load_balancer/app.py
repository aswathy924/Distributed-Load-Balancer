from flask import Flask, jsonify
from flask_cors import CORS
import requests
import time
from algorithms import LoadBalancer
from metrics import metrics
from threading import Thread
from health_check import monitor_servers

app = Flask(__name__)
CORS(app)

VALID_ALGOS = ["round_robin", "least_connections", "random"]

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
    else:
        return lb.random()

@app.route("/")
def route_request():
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
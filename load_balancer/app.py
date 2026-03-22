from flask import Flask, jsonify
import requests
from algorithms import LoadBalancer

app = Flask(__name__)

servers = [
    "http://backend1:5000",
    "http://backend2:5000",
    "http://backend3:5000"
]

lb = LoadBalancer(servers)
ALGO = "round_robin"

def get_server():
    if ALGO == "round_robin":
        return lb.round_robin()
    elif ALGO == "least_connections":
        return lb.least_connections()
    else:
        return lb.random()

@app.route("/")
def route_request():
    server = get_server()
    try:
        response = requests.get(server)
        return jsonify(response.json())
    except:
        return {"error": "Server down"}, 500

@app.route("/set_algorithm/<algo>")
def set_algo(algo):
    global ALGO
    ALGO = algo
    return {"message": f"Algorithm set to {algo}"}
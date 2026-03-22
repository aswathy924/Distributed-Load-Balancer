from flask import Flask, render_template
from flask_cors import CORS
import sys
import os
import requests

# # Adds the parent directory to the search path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from load_balancer.metrics import metrics

app = Flask(__name__)
CORS(app)

@app.route("/")
def dashboard():
    try:
        data = requests.get("http://localhost:5000/metrics").json()
    except:
        data = {"servers": {}, "algorithm": "N/A", "uptime": 0}

    return render_template("dashboard.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=7000)
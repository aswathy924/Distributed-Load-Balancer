from flask import Flask
from flask_cors import CORS
import socket
import random
import time
import sys

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    time.sleep(random.uniform(0.1, 0.5))  # simulate load
    return {
        "server": socket.gethostname(),
        "status": "OK"
    }

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host="0.0.0.0", port=port)
from flask import Flask
import socket
import random
import time

app = Flask(__name__)

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
    app.run(host="0.0.0.0", port=5000)
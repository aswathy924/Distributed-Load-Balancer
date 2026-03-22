from flask import Flask, jsonify
import sys
import time
import random

def create_app(server_id):
    app = Flask(__name__)

    @app.route("/")
    def handle_request():
        # Simulate different server speeds
        if server_id == 1:
            time.sleep(1)   # slow server 1
        else:
            time.sleep(0.2)  # faster servers

        return jsonify({
            "server_id": server_id,
            "message": f"Response from Server {server_id}"
        })

    @app.route("/health")
    def health():
        return jsonify({
            "server_id": server_id,
            "status": "healthy"
        })

    return app


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <server_id>")
        sys.exit(1)

    server_id = int(sys.argv[1])
    port = 5000 + server_id

    app = create_app(server_id)

    print(f"Starting Server {server_id} on port {port}")
    app.run(host="0.0.0.0", port=port)

    
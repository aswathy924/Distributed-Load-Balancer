from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def dashboard():
    # The frontend is fully decoupled. All metrics fetching is handled by the browser.
    # This prevents Docker internal networking problems where "localhost" points to the dashboard container itself.
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
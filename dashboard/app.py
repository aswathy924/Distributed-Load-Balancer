from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def dashboard():
    # The frontend is fully decoupled. All metrics fetching is handled by the browser.
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
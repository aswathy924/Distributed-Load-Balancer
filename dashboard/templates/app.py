from flask import Flask, render_template
from load_balancer.metrics import metrics

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html", data=metrics)

@app.route("/data")
def data():
    return metrics.get_stats()

if __name__ == "__main__":
    app.run(port=7000)
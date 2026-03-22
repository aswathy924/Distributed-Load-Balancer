import requests
import matplotlib.pyplot as plt

URL = "http://127.0.0.1:8000/metrics"

def fetch_metrics():
    response = requests.get(URL)
    return response.json()

def plot_requests(data, title):
    servers = list(data.keys())
    requests_count = [data[s]["requests"] for s in servers]

    plt.figure()
    plt.bar(servers, requests_count)
    plt.title(f"Requests Distribution - {title}")
    plt.xlabel("Servers")
    plt.ylabel("Number of Requests")
    plt.xticks(rotation=30)
    plt.show()

def plot_response_time(data, title):
    servers = list(data.keys())
    times = [data[s]["avg_response_time"] for s in servers]

    plt.figure()
    plt.bar(servers, times)
    plt.title(f"Avg Response Time - {title}")
    plt.xlabel("Servers")
    plt.ylabel("Seconds")
    plt.xticks(rotation=30)
    plt.show()

if __name__ == "__main__":
    data = fetch_metrics()

    algo = input("Enter algorithm name (RR / LC): ")

    plot_requests(data, algo)
    plot_response_time(data, algo)
import threading
import time
import requests

class HealthMonitor:
    def __init__(self, servers, interval=5):
        self.all_servers = servers
        self.healthy_servers = servers.copy()
        self.interval = interval
        self.lock = threading.Lock()

    def check_server(self, server):
        try:
            response = requests.get(f"{server}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def run(self):
        while True:
            new_healthy = []

            for server in self.all_servers:
                if self.check_server(server):
                    new_healthy.append(server)

            with self.lock:
                self.healthy_servers = new_healthy

            print(f"Healthy servers: {self.healthy_servers}")

            time.sleep(self.interval)

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def get_healthy_servers(self):
        with self.lock:
            return self.healthy_servers.copy()
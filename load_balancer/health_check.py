import requests
import time

def monitor_servers(lb):
    while True:
        for server in list(lb.servers):
            try:
                requests.get(server + "/health", timeout=1)
            except:
                print(f"{server} is down. Removing...")
                lb.servers.remove(server)
        time.sleep(5)
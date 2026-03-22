import time
import requests
from metrics import metrics


def monitor_servers(lb):
    # Store all original servers
    all_servers = list(lb.servers)

    while True:
        for server in all_servers:

            try:
                response = requests.get(server + "/health", timeout=1)

                #  If server is alive and NOT in active list → RE-ADD
                if response.status_code == 200:
                    if server not in lb.servers:
                        print(f"{server} is back ONLINE. Re-adding...")
                        lb.servers.append(server)
                        lb.connections[server] = 0

                    #  mark as UP
                    metrics.record(server, 0, success=True, is_health_check=True)

            except:
                if server in lb.servers:
                    print(f"{server} is DOWN. Removing...")
                    lb.servers.remove(server)

                    lb.index = 0

                    if server in lb.connections:
                        del lb.connections[server]

                #  IMPORTANT: mark as DOWN in metrics
                metrics.record(server, 0, success=False, is_health_check=True)

        time.sleep(2)  # check every 2 seconds
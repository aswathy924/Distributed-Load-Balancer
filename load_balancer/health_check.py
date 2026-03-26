import asyncio
import httpx
from metrics import metrics
from algorithms import LoadBalancer
from config import settings

async def monitor_servers(lb: LoadBalancer):
    """
    Continuously monitors backend servers through asynchronous HTTP checks.
    Automatically re-adds them to the load balancing pool when they come back up.
    """
    while True:
        # Track all dynamically known servers
        current_servers = list(lb.all_registered_servers)

        async with httpx.AsyncClient(timeout=1.0) as client:
            for server in current_servers:
                # Protect against the server being deleted right as this loop begins
                if server not in lb.all_registered_servers:
                    continue

                try:
                    # Request the health endpoint asynchronously
                    response = await client.get(f"{server}/health")
                    is_success = response.status_code == 200

                    # Protect against the server being deleted while waiting for HTTP response
                    if server not in lb.all_registered_servers:
                        continue

                    # If server is alive and NOT in active list -> RE-ADD
                    if server not in lb.servers:
                        print(f"[HEALTH] {server} is back ONLINE. Re-adding...")
                        lb.add_server(server)

                    # Mark as UP in global metrics
                    await metrics.record(server, 0.0, success=True, is_health_check=True)

                except Exception:
                    # Failed health check, remove the server
                    if server in lb.servers:
                        print(f"[HEALTH] {server} is DOWN. Removing from active routing pool...")
                        lb.remove_server(server)

                    # Protect against creating a ghost-metrics entry for a deleted server
                    if server in lb.all_registered_servers:
                        await metrics.record(server, 0.0, success=False, is_health_check=True)

            # Wait 2 seconds before the next sweep
            await asyncio.sleep(2)
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
    # Track all known servers
    all_servers = list(settings.SERVERS)

    async with httpx.AsyncClient(timeout=1.0) as client:
        while True:
            for server in all_servers:
                try:
                    # Request the health endpoint asynchronously
                    response = await client.get(f"{server}/health")
                    response.raise_for_status()

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

                    # Mark as DOWN in global metrics
                    await metrics.record(server, 0.0, success=False, is_health_check=True)

            # Wait 2 seconds before the next sweep
            await asyncio.sleep(2)
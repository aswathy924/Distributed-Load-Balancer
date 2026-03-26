import asyncio
import time
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import httpx

from algorithms import LoadBalancer
from metrics import metrics
from health_check import monitor_servers
from config import settings

app = FastAPI(title="Distributed Load Balancer API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
lb = LoadBalancer(list(settings.SERVERS))
ALGO = settings.DEFAULT_ALGO

@app.on_event("startup")
async def startup_event():
    # Start the background health check task
    asyncio.create_task(monitor_servers(lb))

def get_server(client_ip: str) -> Optional[str]:
    """Retrieves the next available backend server based on the active algorithm."""
    # Ensure current algorithm is logged to metrics
    if ALGO == "round_robin":
        return lb.round_robin()
    elif ALGO == "least_connections":
        return lb.least_connections()
    elif ALGO == "random":
        return lb.random()
    elif ALGO == "weighted":
        return lb.weighted_round_robin()
    elif ALGO == "power_of_two":
        return lb.power_of_two()
    elif ALGO == "consistent_hashing":
        return lb.consistent_hashing(client_ip)
    
    return lb.round_robin()

# Define API routes BEFORE the catch-all proxy routes

@app.get("/set_algorithm/{algo}")
async def set_algo(algo: str):
    """Sets the active routing algorithm."""
    global ALGO

    if algo not in settings.VALID_ALGOS:
        raise HTTPException(status_code=400, detail=f"Choose from {settings.VALID_ALGOS}")

    ALGO = algo
    await metrics.set_algorithm(algo)
    return {"message": f"Algorithm set to {algo}"}

@app.get("/get_algorithm")
async def get_algo():
    """Gets the active routing algorithm."""
    return {"current_algorithm": ALGO}

@app.get("/metrics")
async def get_metrics():
    """Returns the current load balancing statistics."""
    return await metrics.get_stats()


# Proxy Routing (Catch-all)

async def proxy_request(request: Request, path: str = ""):
    """
    Acts as the reverse proxy, forwarding client requests to the chosen backend server asynchronously.
    """
    if not lb.servers:
        raise HTTPException(status_code=500, detail="No backend servers available")

    client_ip = request.client.host
    
    # We will try servers until one succeeds or we've tried as many times as there are active servers
    for _ in range(len(lb.servers)):
        server = get_server(client_ip)
        
        if not server:
            continue

        try:
            lb.increment(server)
            start_time = time.time()

            # Forward the request asynchronously
            async with httpx.AsyncClient() as client:
                query = request.url.query
                url_path = f"/{path}" if path else "/"
                url = f"{server}{url_path}" + (f"?{query}" if query else "")
                
                # Fetching the body for non-GET requests
                body = await request.body()
                
                # Exclude 'host' header to avoid conflict, and 'content-length' which httpx recalculates
                headers = dict(request.headers)
                headers.pop("host", None)
                headers.pop("content-length", None)

                response = await client.request(
                    method=request.method,
                    url=url,
                    content=body,
                    headers=headers,
                    timeout=2.0
                )

            response_time = time.time() - start_time
            lb.decrement(server)

            # Record metrics
            await metrics.record(server, response_time, success=True)
            await metrics.set_algorithm(ALGO)

            # Return the response mimicking the backend
            return Response(
                content=response.content,
                status_code=response.status_code,
                # remove headers that can cause issues
                headers={k: v for k, v in response.headers.items() if k.lower() not in ("content-encoding", "content-length", "transfer-encoding")}
            )

        except Exception as exc:
            print(f"[ERROR] {server} failed: {exc}")
            lb.decrement(server)
            
            # Record failure
            await metrics.record(server, 0.0, success=False)
            
            # Remove failed server dynamically
            lb.remove_server(server)

    raise HTTPException(status_code=500, detail="All backend servers failed")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_request_with_path(request: Request, path: str):
    return await proxy_request(request, path)

@app.api_route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def route_root_request(request: Request):
    return await proxy_request(request, "")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=True)
import asyncio
import httpx
import time

LOAD_BALANCER_URL = "http://127.0.0.1:5000"
NUM_REQUESTS = 500  # Increased to show asynchronous load handling

async def send_request(client, i):
    try:
        response = await client.get(LOAD_BALANCER_URL)
        data = response.json()
        print(f"Request {i} -> {data.get('server')}")
        return True
    except Exception as e:
        print(f"Request {i} failed: {e}")
        return False

async def main():
    print(f"Starting {NUM_REQUESTS} asynchronous requests to the Load Balancer...")
    start_time = time.time()
    
    # Use connection pooling to simulate high concurrency
    limits = httpx.Limits(max_connections=200)
    async with httpx.AsyncClient(limits=limits, timeout=10.0) as client:
        tasks = [send_request(client, i) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    success_count = sum(results)

    print("\n===== RESULTS =====")
    print(f"Total Requests: {NUM_REQUESTS}")
    print(f"Successful: {success_count}")
    print(f"Failed: {NUM_REQUESTS - success_count}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    asyncio.run(main())
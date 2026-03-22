import requests
import time
from concurrent.futures import ThreadPoolExecutor

LOAD_BALANCER_URL = "http://127.0.0.1:8000"
NUM_REQUESTS = 50


def send_request(i):
    try:
        response = requests.get(LOAD_BALANCER_URL)
        data = response.json()
        print(f"Request {i} → {data['server_id']}")
        return True
    except Exception as e:
        print(f"Request {i} failed: {e}")
        return False


if __name__ == "__main__":
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(send_request, range(NUM_REQUESTS)))

    end_time = time.time()

    success_count = sum(results)

    print("\n===== RESULTS =====")
    print(f"Total Requests: {NUM_REQUESTS}")
    print(f"Successful: {success_count}")
    print(f"Failed: {NUM_REQUESTS - success_count}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")
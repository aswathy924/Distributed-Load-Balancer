from locust import HttpUser, task, between

class LoadBalancerUser(HttpUser):
    """
    Simulates a real-world client hitting the load balancer.
    """
    # Wait time between tasks simulating "thinking time" of a real user
    wait_time = between(0.1, 0.5)

    @task
    def access_load_balancer(self):
        # We perform a GET request against the root path handling index logic
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with {response.status_code}")

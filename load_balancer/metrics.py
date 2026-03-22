import threading
import time

class Metrics:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

        #  NEW: global system info
        self.algorithm = "round_robin"
        self.start_time = time.time()

    def record(self, server, response_time, success=True):
        with self.lock:
            if server not in self.data:
                self.data[server] = {
                    "requests": 0,
                    "failures": 0,
                    "total_time": 0
                }

            self.data[server]["requests"] += 1
            self.data[server]["total_time"] += response_time

            if not success:
                self.data[server]["failures"] += 1

    #  NEW: update algorithm
    def set_algorithm(self, algo):
        with self.lock:
            self.algorithm = algo

    #  NEW: get full stats (dashboard ready)
    def get_stats(self):
        with self.lock:
            result = {}

            for server, stats in self.data.items():
                avg_time = (
                    stats["total_time"] / stats["requests"]
                    if stats["requests"] > 0 else 0
                )

                result[server] = {
                    "requests": stats["requests"],
                    "failures": stats["failures"],
                    "avg_response_time": round(avg_time, 3)
                }

            return {
                "servers": result,
                "algorithm": self.algorithm,
                "uptime": round(time.time() - self.start_time, 2)
            }

    #  OPTIONAL: reset metrics (useful for testing)
    def reset(self):
        with self.lock:
            self.data = {}
            self.start_time = time.time()


#  VERY IMPORTANT: global instance (used in app.py)
metrics = Metrics()
import threading
import time

class Metrics:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

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

            return result
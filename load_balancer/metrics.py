import asyncio
import time
from typing import Dict, Any

from config import settings

class Metrics:
    """
    A thread-safe metrics collector for load balancing statistics.
    Designed for async execution via asyncio locks.
    """
    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()

        # Global system info
        self.algorithm = settings.DEFAULT_ALGO
        self.start_time = time.time()

    async def record(self, server: str, response_time: float, success: bool = True, is_health_check: bool = False):
        """
        Record a request mapping to a server asynchronously.
        """
        async with self.lock:
            if server not in self.data:
                self.data[server] = {
                    "requests": 0,
                    "failures": 0,
                    "total_time": 0,
                    "status": "UP"
                }

            # Skip request count for health checks
            if not is_health_check:
                self.data[server]["requests"] += 1
                self.data[server]["total_time"] += response_time

            if not success:
                self.data[server]["failures"] += 1
                self.data[server]["status"] = "DOWN"
            else:
                self.data[server]["status"] = "UP"

    async def set_algorithm(self, algo: str):
        """Update the active routing algorithm."""
        async with self.lock:
            self.algorithm = algo

    async def get_stats(self) -> Dict[str, Any]:
        """Fetch full diagnostic report (used by Dashboard)."""
        async with self.lock:
            result = {}

            for server, stats in self.data.items():
                avg_time = (
                    stats["total_time"] / stats["requests"]
                    if stats["requests"] > 0 else 0
                )

                result[server] = {
                    "requests": stats["requests"],
                    "failures": stats["failures"],
                    "avg_response_time": round(avg_time, 3),
                    "status": stats.get("status", "UNKNOWN")   
                }

            return {
                "servers": result,
                "algorithm": self.algorithm,
                "uptime": round(time.time() - self.start_time, 2)
            }

    async def reset(self):
        """Resets the statistics."""
        async with self.lock:
            self.data = {}
            self.start_time = time.time()


# Global instance imported by the API
metrics = Metrics()
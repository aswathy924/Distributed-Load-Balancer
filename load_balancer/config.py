import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Global configuration for the Load Balancer using environment variables.
    """
    # The port the load balancer will listen on
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Default backend servers in case they are not discovered
    SERVERS: List[str] = [
        "http://backend1:5000",
        "http://backend2:5000",
        "http://backend3:5000"
    ]

    # Allowed load balancing algorithms
    VALID_ALGOS: List[str] = [
        "round_robin",
        "least_connections",
        "random",
        "weighted",
        "power_of_two",
        "consistent_hashing"
    ]

    DEFAULT_ALGO: str = "round_robin"

settings = Settings()

import random
import hashlib
from bisect import bisect
from typing import List, Optional

class LoadBalancer:
    """
    A professional-grade Load Balancer implementing various routing algorithms.
    """
    def __init__(self, servers: List[str]):
        """
        Initialize the load balancer with a list of backend servers.

        Args:
            servers (List[str]): A list of server URLs (e.g. 'http://backend1:5000')
        """
        self.servers = servers
        self.all_registered_servers = set(servers)
        self.index = 0
        self.connections = {server: 0 for server in servers}

        # For weighted round robin
        self.weights = {server: 1 for server in servers}
        self.weighted_list = self._build_weighted_list()

        # For consistent hashing
        self.virtual_nodes = 100 
        self.hash_ring = {}
        self.sorted_keys = []
        self._build_hash_ring()

    # ---------------- BASIC LOGIC ---------------- #

    def add_server(self, server: str):
        """Add a server dynamically to the pool."""
        self.all_registered_servers.add(server)
        if server not in self.servers:
            self.servers.append(server)
            self.connections[server] = 0
            self.weights[server] = 1
            self.weighted_list = self._build_weighted_list()
            self._add_node_to_ring(server)

    def remove_server(self, server: str):
        """Temporarily remove a server from the active routing pool (e.g. failed health check)."""
        if server in self.servers:
            self.servers.remove(server)
            if server in self.connections:
                del self.connections[server]
            if server in self.weights:
                del self.weights[server]
            self.weighted_list = self._build_weighted_list()
            self._remove_node_from_ring(server)
            self.index = 0

    def unregister_server(self, server: str):
        """Permanently remove a server from tracking entirely across the whole system."""
        self.remove_server(server)
        if server in self.all_registered_servers:
            self.all_registered_servers.remove(server)

    # ---------------- ALGORITHMS ---------------- #

    def round_robin(self) -> Optional[str]:
        """Distributes requests equally across all servers in order."""
        if not self.servers:
            return None

        self.index = self.index % len(self.servers)
        server = self.servers[self.index]
        self.index += 1
        return server

    def random(self) -> Optional[str]:
        """Routes requests completely randomly."""
        return random.choice(self.servers) if self.servers else None

    def least_connections(self) -> Optional[str]:
        """Routes requests to the server with the fewest active connections."""
        if not self.connections:
            return None
        return min(self.connections, key=self.connections.get)

    def power_of_two(self) -> Optional[str]:
        """Samples two servers and picks the one with fewer connections."""
        if len(self.servers) < 2:
            return self.random()

        s1, s2 = random.sample(self.servers, 2)
        return s1 if self.connections[s1] < self.connections[s2] else s2

    # ---------------- WEIGHTED ---------------- #

    def _build_weighted_list(self) -> List[str]:
        """Rebuilds the weighted array used for weighted round-robin."""
        weighted = []
        for server, weight in self.weights.items():
            weighted.extend([server] * weight)
        return weighted

    def weighted_round_robin(self) -> Optional[str]:
        """Distributes requests proportional to assigned weights."""
        if not self.weighted_list:
            return self.random()

        server = self.weighted_list[self.index % len(self.weighted_list)]
        self.index += 1
        return server

    # ---------------- CONSISTENT HASHING ---------------- #

    def _hash(self, key: str) -> int:
        """MD5 Hash function for mapping points onto the ring."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def _build_hash_ring(self):
        """Initializes the hash ring based on active servers."""
        self.hash_ring.clear()
        self.sorted_keys.clear()
        for server in self.servers:
            self._add_node_to_ring(server)

    def _add_node_to_ring(self, server: str):
        """Adds virtual nodes for a server to the ring."""
        for i in range(self.virtual_nodes):
            replica_key = self._hash(f"{server}:{i}")
            self.hash_ring[replica_key] = server
            self.sorted_keys.append(replica_key)
        self.sorted_keys.sort()

    def _remove_node_from_ring(self, server: str):
        """Removes all virtual nodes for a server from the ring."""
        for i in range(self.virtual_nodes):
            replica_key = self._hash(f"{server}:{i}")
            if replica_key in self.hash_ring:
                del self.hash_ring[replica_key]
                self.sorted_keys.remove(replica_key)

    def consistent_hashing(self, client_ip: str = None) -> Optional[str]:
        """Routes requests based on a hash of the client identifier (e.g. IP)."""
        if not self.hash_ring:
            return None
            
        # If no client IP provided, just pick a random hash point
        if not client_ip:
            client_ip = str(random.random())

        hash_val = self._hash(client_ip)
        
        # Find the first node on the ring strictly greater than hash_val
        idx = bisect(self.sorted_keys, hash_val)
        
        # Wrap around to the start of the ring if we hit the end
        if idx == len(self.sorted_keys):
            idx = 0
            
        node_hash = self.sorted_keys[idx]
        return self.hash_ring[node_hash]

    # ---------------- CONNECTION TRACKING ---------------- #

    def increment(self, server: str):
        """Tracks an active request dispatched to the server."""
        if server in self.connections:
            self.connections[server] += 1

    def decrement(self, server: str):
        """Marks a request as completed, decreasing the connection counter."""
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1
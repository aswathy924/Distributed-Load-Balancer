import random

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0
        self.connections = {server: 0 for server in servers}

        # NEW: weights (you can tweak)
        self.weights = {server: 1 for server in servers}

        # For weighted round robin
        self.weighted_list = self._build_weighted_list()

    # ---------------- BASIC ---------------- #

    def round_robin(self):
        if not self.servers:
            return None

        self.index = self.index % len(self.servers)   # ✅ FIX

        server = self.servers[self.index]
        self.index += 1

        return server

    def random(self):
        return random.choice(self.servers)

    def least_connections(self):
        return min(self.connections, key=self.connections.get)

    # ---------------- WEIGHTED ---------------- #

    def _build_weighted_list(self):
        weighted = []
        for server, weight in self.weights.items():
            weighted.extend([server] * weight)
        return weighted

    def weighted_round_robin(self):
        if not self.weighted_list:
            return random.choice(self.servers)

        server = self.weighted_list[self.index % len(self.weighted_list)]
        self.index += 1
        return server

    # ---------------- ADVANCED ---------------- #

    def power_of_two(self):
        if len(self.servers) < 2:
            return self.random()

        s1, s2 = random.sample(self.servers, 2)

        # pick server with fewer active connections
        return s1 if self.connections[s1] < self.connections[s2] else s2

    # ---------------- CONNECTION TRACKING ---------------- #

    def increment(self, server):
        if server in self.connections:
            self.connections[server] += 1

    def decrement(self, server):
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1
import random

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0
        self.connections = {s: 0 for s in servers}

    def round_robin(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server

    def random(self):
        return random.choice(self.servers)

    def least_connections(self):
        return min(self.connections, key=self.connections.get)
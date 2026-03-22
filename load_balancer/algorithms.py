class RoundRobin:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0

    def get_next_server(self):
        if not self.servers:
            return None

        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server
    
class LeastConnections:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {server: 0 for server in servers}

    def update_servers(self, servers):
        # Add new servers if needed
        for server in servers:
            if server not in self.connections:
                self.connections[server] = 0

        # Remove dead servers
        for server in list(self.connections.keys()):
            if server not in servers:
                del self.connections[server]

        self.servers = servers

    def get_next_server(self):
        if not self.servers:
            return None

        # Pick server with least active connections
        server = min(self.connections, key=self.connections.get)
        self.connections[server] += 1
        return server

    def release_connection(self, server):
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1
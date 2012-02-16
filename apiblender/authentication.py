class AuthenticationManager:
    """Ensure authentication."""

    def __init__(self):
        self.servers = {}


    def add_server(self, server):
        if server.name not in self.servers:
            parameters = server.authentication.request_parameters(
                                                                server.host,
                                                                server.port)
            if parameters:
                self.servers.update({ server.name: {
                                             "parameters": parameters }})
                return True
            else:
                print("ERROR, authentication failed for server: %s." %\
                        server.name)
                print("> Please check your authentication \
                        configuration. Server not created.")
                return None

    def exists_server(self, server):
        return (server.name in self.servers)

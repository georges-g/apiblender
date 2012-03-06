from datetime import datetime

class PolicyManager:
    """ Limit request when needed """

    def __init__(self):
        self.servers_status = {}

    def add_server(self, server):
        if server.name not in self.servers_status:
            self.servers_status.update({ server.name: {
                                            "request_count": 0, 
                                            "sleeping_state": False,
                                            "sleeping_since": None } })
        
    def signal_server_request(self, server):
        self.servers_status[server.name]["request_count"] += 1
    
    def signal_too_many_calls(self, server):
        print "WARNING: Too many calls for %s" % server.name
        self.servers_status[server.name]["sleeping_state"] = True
        if not self.servers_status[server.name]["sleeping_since"]:
            self.servers_status[server.name]["sleeping_since"] = datetime.now()

    def signal_wrong_response_code(self, server, code):
        #TODO: what to do w the code?
        print "WARNING: Wrong response status for %s" % server.name
        self.servers_status[server.name]["sleeping_state"] = True
        if not self.servers_status[server.name]["sleeping_since"]:
            self.servers_status[server.name]["sleeping_since"] = datetime.now()


    def get_server_request_count(self, server):
        return self.servers_status[server.name]["request_count"]

    def get_request_permission(self, server):
        if self.servers_status[server.name]["sleeping_state"]:
            return False
        elif (self.servers_status[server.name]["request_count"]
                    >= server.policy.requests_per_hour):
            self.servers_status[server.name]["sleeping_state"] = True
            self.servers_status[server.name]["sleeping_since"] = datetime.now()
            return False
        else:
            return True

    def get_sleeping_time(self, server):
        if not self.servers_status[server.name]["sleeping_state"]:
            return 0
        else:
            return server.policy.too_many_calls_waiting_seconds

    def reset_server_sleep(self, server):
        self.servers_status[server.name]["sleeping_state"] = False
        self.servers_status[server.name]["sleeping_since"] = None 
        self.servers_status[server.name]["request_count"] = 0


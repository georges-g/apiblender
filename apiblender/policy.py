import logging
from datetime import datetime

logger = logging.getLogger('apiblender')

class PolicyManager:
    """ Limit request when needed """
    # 
    # TODO: the request counter is not properly implemented, it should be
    # resetted periodically. 
    # So far, it sleeps only if a too many cally calls status is
    # received, it seems to work.
    #
    def __init__(self):
        self.servers_status = {}

    def load_server(self, server):
        # Updates servers_status
        if server.name not in self.servers_status:
            self.servers_status.update({ server.name: {
                                            "request_count": 0, 
                                            "sleeping_state": False,
                                            "sleeping_since": None } })
        
    def signal_server_request(self, server):
        self.servers_status[server.name]["request_count"] += 1
    
    def signal_too_many_calls(self, server):
        logger.warning("Too many calls for %s" % server.name)
        # Blender goes to sleep
        self.servers_status[server.name]["sleeping_state"] = True
        if not self.servers_status[server.name]["sleeping_since"]:
            self.servers_status[server.name]["sleeping_since"] = datetime.now()

    def signal_wrong_response_status(self, server, status):
        #TODO: Something else could happen with the wrong status
        logger.warning(    "Wrong response status:%s for %s" % \
                            (status, server.name) )

    def get_server_request_count(self, server):
        return self.servers_status[server.name]["request_count"]

    def get_request_permission(self, server):
        # Checks the servers_status to see if it can make the request 
        if self.servers_status[server.name]["sleeping_state"]:
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


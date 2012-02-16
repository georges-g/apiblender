import os
import sys
import json
import urllib
import httplib

import server
import policy
import authentication

GENERAL_CONFIG = os.path.dirname(__file__) + "/config/general.json"

class Blender:
    """You have to create one."""


    def __init__(self):

        # Load the configuration file
        if not os.path.exists(GENERAL_CONFIG):
            sys.exit('ERROR: File %s was not found!' % GENERAL_CONFIG)
        with open(GENERAL_CONFIG, 'r') as config_file:
            general_config = json.load(config_file)
        
        self.user_agent = general_config["user-agent"]
        self.apis_path = os.path.dirname(__file__) + general_config["apis_path"] 

        self.policy_manager = policy.PolicyManager()
        self.authentication_manager = authentication.AuthenticationManager()

        self.server = None
        self.interaction = None


    def list_servers(self):
        """List available servers."""

        for filename in os.listdir(self.apis_path):
            print filename.split('.json')[0]


    def load_server(self, server_name):
        """Create a server instance."""
    
        server_config_path = self.apis_path + server_name + '.json'

        if not os.path.exists(server_config_path):
            print('ERROR: File %s was not found.' % server_config_path)
        else:
            with open(server_config_path, 'r') as server_config_file:
                server_config = json.load(server_config_file)

            self.server = server.Server(server_config)

            if self.server.policy:
                self.policy_manager.add_server(self.server)
            
            if self.server.authentication:
                self.authentication_manager.add_server(self.server)


    def load_interaction(self, interaction_name):

        if not self.server:
            print('ERROR: You must load a server first.' % interaction_name)

        elif interaction_name in [interaction.name for interaction in
                    self.server.interactions]:
                self.interaction = interaction
        else:
            print('ERROR: Interaction %s was not found.' % interaction_name)


    def blend(self, request_parameters):

        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time()
            print "sleeping for: %s seconds" % (sleeping_time)
            time.sleep(sleeping_time)

        #TODO: request_parameters verification
    
        total_parameters = {}
        total_parameters.update(self.interaction.request.path_constant_parameters)
        total_parameters.update(request_parameters)

        total_path = "%s?%s" % (self.interaction.request.root_path, 
                                urllib.urlencode(total_parameters))

        #TODO: HTTP or HTTPS? 
        c = httplib.HTTPConnection(self.server.host, self.server.port)

        print "> Request: %s%s" % (self.server.host, total_path) 
        c.request(self.interaction.request.method, total_path)
        r = c.getresponse()
        http_response = r.read()
        c.close()
        
        print http_response 



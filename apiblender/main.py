import os
import sys
import json
import urllib
import httplib

import serverclasses
import policy
import auth

GENERAL_CONFIG = os.path.dirname(__file__) + "/config/general.json"

class Blender:
    """You have to create one."""

    def __init__(self):
        self.load_config_file()
        self.policy_manager = policy.PolicyManager()
        self.auth_manager = auth.AuthManager()
        self.server = None
        self.interaction = None

    def load_config_file(self):
        if not os.path.exists(GENERAL_CONFIG):
            sys.exit('ERROR: File %s was not found!' % GENERAL_CONFIG)
        with open(GENERAL_CONFIG, 'r') as config_file:
            general_config = json.load(config_file)
        self.user_agent = general_config["user-agent"]
        self.apis_path = os.path.dirname(__file__) + general_config["apis_path"] 
        
    def list_servers(self):
        """List available servers."""
        for filename in os.listdir(self.apis_path):
            print filename.split('.json')[0]

    def load_server(self, server_name):
        server_config_path = self.apis_path + server_name + '.json'
        if not os.path.exists(server_config_path):
            print('ERROR: File %s was not found.' % server_config_path)
        else:
            with open(server_config_path, 'r') as server_config_file:
                server_config = json.load(server_config_file)
            self.server = serverclasses.Server(server_config)
            if self.server.policy:
                self.policy_manager.add_server(self.server)
            if self.server.auth:
                if not self.auth_manager.add_server(self.server):
                    self.server = None

    def load_interaction(self, interaction_name):
        if not self.server:
            print('ERROR loading %s: no server loaded.' % interaction_name)
            return None
        if interaction_name in [interaction.name for interaction in
                    self.server.interactions]:
                self.interaction = interaction
        else:
            print('ERROR loading %s: not found on server %s.'\
                    % (interaction_name, self.server.name))
            return None

    def blend(self, request_parameters):
        if not self.interaction:
            print('ERROR blending: no interaction loaded.')
            return None
        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time()
            print "sleeping for: %s seconds" % (sleeping_time)
            time.sleep(sleeping_time)
        response = self.make_request(request_parameters)
        ready_response = self.prepare_response(response)
        print str(ready_response)[0:100]
        return ready_response

    def make_request(self, request_parameters):
        #TODO: request_parameters verification
        total_parameters = {}
        total_parameters.update(
                self.interaction.request.path_constant_parameters)
        total_parameters.update(request_parameters)

        if self.auth_manager.exists_server(self.server):
            total_parameters.update(
                    auth_manager.servers["server.name"])
            c = httplib.HTTPSConnection(self.server.host, self.server.port,
                                        timeout = 10)
        else:
            c = httplib.HTTPConnection(self.server.host, self.server.port,
                                       timeout = 10)

        total_path = "%s?%s" % (self.interaction.request.root_path, 
                                urllib.urlencode(total_parameters))

        print "> Request: %s%s" % (self.server.host, total_path) 
        c.request(self.interaction.request.method, total_path)
        r = c.getresponse()
        response = r.read()
        c.close()
        return response

    def prepare_response(self, response):
        try:
            #TODO json or xml
            response = json.loads(response)
        except Exception:
            #TODO manage exception
            print 'wrong results'
            return False
        if self.interaction.response.extractor:
            ready_response = \
                self.interaction.response.extractor.extract(response)
        else:
            ready_response = response
        return ready_response

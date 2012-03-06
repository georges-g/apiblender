import os
import sys
import json
import urllib
import httplib
import time

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
            self.server = None
        else:
            with open(server_config_path, 'r') as server_config_file:
                server_config = json.load(server_config_file)
            self.server = serverclasses.Server(server_config)
            if self.server.policy:
                self.policy_manager.add_server(self.server)
            if self.server.auth:
                if not self.auth_manager.add_server(self.server):
                    self.server = None

    def list_interactions(self):
        for interaction in self.server.interactions:
            print interaction.name

    def load_interaction(self, interaction_name):
        if not self.server:
            print('ERROR loading %s: no server loaded.' % interaction_name)
            self.interaction = None
            return None
        for avb_interaction in self.server.interactions:
            if interaction_name == avb_interaction.name:
                self.interaction = avb_interaction
                return
        else:
            print('ERROR loading %s: not found on server %s.'\
                    % (interaction_name, self.server.name))
            self.interaction = None
            return None

    def list_parameters(self):
        """List available servers."""
        for parameter in self.interaction.request.parameters:
            print parameter 

    def set_parameters(self, parameters_to_set):
        if not self.interaction:
            print('ERROR setting parameters: no interaction loaded.')
            return None
        for k, v in parameters_to_set.iteritems():
            self.interaction.request.set_parameter([k,v])

    def blend(self):
        if not self.interaction:
            print('ERROR blending: no interaction loaded.')
            return None
        status = None
        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time(self.server)
            print "WARNING: Sleeping for: %s seconds" % (sleeping_time)
            time.sleep(sleeping_time)
            self.policy_manager.reset_server_sleep(self.server)
        content, status = self.make_request()
        ready_content = self.prepare_content(content)
        self.check_response(status)
        print str(ready_content)[0:100]
        return ready_content 

    def make_request(self):
        total_parameters = self.interaction.request.get_total_parameters()
        # TODO: authmanager method
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
        response = c.getresponse()
        content = response.read()
        status = response.status
        c.close()
        self.policy_manager.signal_server_request(self.server)
        # TODO: return whole object, clone?
        return content, status 
    
    def check_response(self, status):
# TODO: check response.read
        if not status:
            return 
        elif status == self.interaction.response.expected_status_code:
            return 
        elif status == self.server.policy.too_many_calls_response_code:
            self.policy_manager.signal_too_many_calls(self.server)
            return 
        else:
            self.policy_manager.signal_wrong_response_code(self.server, 
                    status)
            return 

    def prepare_content(self, content):
        #try:
        #TODO JSON or XML
        content = json.loads(content)
        #except Exception:
            #TODO manage exception
        #print 'wrong results'
        #    return False
        if self.interaction.response.extractor:
            ready_content = \
                self.interaction.response.extractor.extract(content)
        else:
            ready_content = content 
        return ready_content

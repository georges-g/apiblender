import sys
import os
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
            self.policy_manager.load_server(self.server)
            self.auth_manager.load_server(self.server)

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

    def list_url_params(self):
        """List available URL parameters."""
        for url_param in self.interaction.request.url_params:
            print url_param 

    def set_url_params(self, url_params_to_set):
        if not self.interaction:
            print('ERROR setting url_params: no interaction loaded.')
            return None
        for k, v in url_params_to_set.iteritems():
            self.interaction.request.set_url_param([k,v])

    def blend(self):
        if not self.interaction:
            print('ERROR blending: no interaction loaded.')
            return None
        #Retries three times
        request_not_made = True
        i = 0
        while request_not_made and i<3:
            try:
                content, headers = self.make_request()
                request_not_made = False
            except Exception:
                i+=1
        if request_not_made:
            print "ERROR: Could not make request"
            print "Server: %s Interaction: %s Parameters: %s" %\
                    (   self.server.name, self.interaction.name,\
                        self.interaction.request.url_params )
            return None
        self.check_response(headers['status'])
        prepared_content = self.prepare_content(content)
        data = {   "raw_content": content,
                   "prepared_content": prepared_content,
                   "headers": headers }
        print "\tStatus code: %s" % (headers['status'])
        print "\tData: %s" % (str(prepared_content)[0:70])
        return data 

    def make_request(self):
        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time(self.server)
            print "WARNING: Sleeping for: %s seconds" % (sleeping_time)
            time.sleep(sleeping_time)
            self.policy_manager.reset_server_sleep(self.server)
        total_url_params = self.interaction.request.get_total_url_params()
        content, headers = self.auth_manager.make_request(  \
                                 self.server, \
                                 self.interaction,   \
                                 total_url_params)
        self.policy_manager.signal_server_request(self.server)
        return content, headers
    
    def check_response(self, status):
# TODO: check response.read
        if not status:
            return False
        elif status == self.interaction.response.expected_status_code:
            return True
        elif status == self.server.policy.too_many_calls_response_code:
            self.policy_manager.signal_too_many_calls(self.server)
            return False
        else:
            self.policy_manager.signal_wrong_response_code(self.server, 
                    status)
            return False

    def prepare_content(self, content):
        #try:
        #TODO JSON or XML
        try:
            content = json.loads(content)
        except Exception:
            return content
        #except Exception:
            #TODO manage exception
        #print 'wrong results'
        #    return False
        if self.interaction.extractor:
            ready_content = \
                self.interaction.extractor.extract(content)
        else:
            ready_content = content 
        return ready_content

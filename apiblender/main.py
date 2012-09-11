import sys
import os
import json
import urllib
import httplib
import time
import logging
import datetime

import xmltodict
import serverclasses
import policy
import auth

GENERAL_CONFIG = os.path.join(   os.path.dirname(__file__), 
                                "config", 
                                "general.json"  )

class Blender:
    """A Blender allows you to make a request after you load a server and an
    interaction. It returns data."""

    def __init__(self):
        self.load_config_file()
        # The policy manager takes care of not making too many requests
        self.policy_manager = policy.PolicyManager()
        # The auth manager takes care of authentication
        self.auth_manager = auth.AuthManager()
        # To make a request, you need to select a server and an interaction
        # belonging to the server
        self.server = None
        self.interaction = None

    def load_config_file(self):
        """ Loads the config file (general.json) """
        if not os.path.exists(GENERAL_CONFIG):
            sys.exit('ERROR: File %s was not found!' % GENERAL_CONFIG)
        with open(GENERAL_CONFIG, 'r') as config_file:
            general_config = json.load(config_file)
        self.user_agent = general_config["user-agent"]
        self.apis_path = os.path.join(os.path.dirname(__file__), general_config["apis_path"])
        
    def list_servers(self):
        """Lists available servers from the config/apis directory """
        for filename in os.listdir(self.apis_path):
            if filename.split('.')[-1] == 'json':
                print filename.split('.json')[0]

    def load_server(self, server_name):
        """ Loads a server """
        server_config_path = os.path.join(self.apis_path, server_name+'.json')
        if not os.path.exists(server_config_path):
            logging.error('File %s was not found.' % server_config_path)
            self.server = None
        else:
            with open(server_config_path, 'r') as server_config_file:
                server_config = json.load(server_config_file)
            self.server = serverclasses.Server(server_config)
            self.policy_manager.load_server(self.server)
            self.auth_manager.load_server(self.server)

    def list_interactions(self):
        """ Lists available interactions for the loaded server """
        for interaction in self.server.interactions:
            print interaction.name

    def load_interaction(self, interaction_name):
        """ Loads an interaction """
        if not self.server:
            logging.error('Loading %s: no server loaded.' % interaction_name)
            self.interaction = None
            return None
        for avb_interaction in self.server.interactions:
            if interaction_name == avb_interaction.name:
                self.interaction = avb_interaction
                return
        else:
            logging.error('Loading %s: not found on server %s.'\
                    % (interaction_name, self.server.name))
            self.interaction = None
            return None

    def list_url_params(self):
        """List available URL parameters for the loaded interaction """
        for url_param in self.interaction.request.url_params:
            print url_param 

    def set_url_params(self, url_params_to_set):
        """ Sets URL parameters, { key1: value1, key2: value2 } """
        if not self.interaction:
            logging.error('Setting url_params: no interaction loaded.')
            return None
        for k, v in url_params_to_set.iteritems():
            self.interaction.request.set_url_param([k,v])

    def blend(self):
        """ Makes a request and return the data, it is currently quite ad
        hoc but it works """
        # Testing if an interaction is properly loaded
        if not self.interaction:
            logging.error('Blending: no interaction loaded.')
            return None
        # Retries to make a request three times
        request_not_made = True
        i = 0
        while request_not_made and i<3:
            try:
                content, headers = self.make_request()
                request_not_made = False
            except Exception:
                i+=1
        if request_not_made:
            logging.error("Could not make request \n" + \
                "Server: %s Interaction: %s" %\
                (self.server.name, self.interaction.name))
            for url_param in self.interaction.request.url_params:
                logging.error("Parameter: %s" % (url_param))
            return None
        # Check the status of the response
        successful_interaction = self.check_status(headers['status'])
        # Loads the content
        loaded_content = self.load_content(content)
        # Define the object the blender returns
        blender_config = {  
            "server": self.server.name,
            "interaction": self.interaction.name,
            "parameters": [url_param.convert_to_dict() for url_param in\
                        self.interaction.request.url_params],
        }
        data = {    "blender_config": blender_config,
                    "timestamp": str(datetime.datetime.now()),
                    "raw_content": content,
                    "loaded_content": loaded_content,
                    "headers": headers,
                    "successful_interaction": successful_interaction}
        logging.info("\tStatus: %s" % (headers['status']) + "\n" + \
                     "\tData: %s" % (str(loaded_content)[0:70]))
        return data 

    def make_request(self):
        """ Called by blend(), it deals with effectively making the
        request """
        # Checking if the policy manager is OK with making a request
        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time(self.server)
            logging.warning("Sleeping for: %s seconds" % (sleeping_time))
            time.sleep(sleeping_time)
            self.policy_manager.reset_server_sleep(self.server)
        # Get the URL parameters
        total_url_params = self.interaction.request.get_total_url_params()
        # Ask the auth_manager to make the request
        content, headers = self.auth_manager.make_request(  \
                                 self.server, \
                                 self.interaction,   \
                                 total_url_params)
        # Signal the request to the policy_manager
        self.policy_manager.signal_server_request(self.server)
        return content, headers
    
    def check_status(self, status):
        """ Checks the response status and signals problems if needed """
        # TODO: checking response.read could be added
        if not status:
            return False
        elif status == self.interaction.response.expected_status:
            return True
        elif status == self.server.policy.too_many_calls_response_status:
            self.policy_manager.signal_too_many_calls(self.server)
            return False
        else:
            self.policy_manager.signal_wrong_response_status(self.server, 
                    status)
            return False

    def load_content(self, content):
        """ Loads the raw content into a python dict """
        if self.interaction.response.serialization_format == "JSON":
            try:
                content = json.loads(content)
            except Exception:
                pass 
        if self.interaction.response.serialization_format == "XML":
            try:
                content = xmltodict.parse(content)
            except Exception:
                pass
        return content
    

import datetime
import json
import logging
import os
import sys
import time

import apiblender.test.config
import xmltodict

import auth
import policy
import serverclasses

logger = logging.getLogger('apiblender')


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
        self.user_agent = None

    def load_config_file(self):
        """ Loads the config file (general.json) """
        if not os.path.exists(apiblender.test.config.general_json_path):
            sys.exit('ERROR: File {} was not found!'.format(apiblender.test.config.general_json_path))
        with open(apiblender.test.config.general_json_path, 'r') as config_file:
            general_config = json.load(config_file)
        self.user_agent = general_config["user-agent"]

    @staticmethod
    def list_servers():
        """Lists available servers from the config/apis directory """
        for filename in os.listdir(apiblender.test.config.apis_folder_path):
            if filename.split('.')[-1] == 'json':
                print filename.split('.json')[0]

    def load_server(self, server_name):
        """ Loads a server """
        server_config_path = os.path.join(apiblender.test.config.apis_folder_path, '{}.json'.format(server_name))
        if os.path.exists(server_config_path) is False:
            logger.error('File {} was not found.'.format(server_config_path))
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
        if self.server is not None:
            logger.error('Loading {}: no server loaded.'.format(interaction_name))
            self.interaction = None
            return None
        for avb_interaction in self.server.interactions:
            if interaction_name == avb_interaction.name:
                self.interaction = avb_interaction
                return
        else:
            logger.error('Loading {}: not found on server %s.'.format(interaction_name, self.server.name))
            self.interaction = None
            return None

    def list_url_params(self):
        """List available URL parameters for the loaded interaction """
        for url_param in self.interaction.request.url_params:
            print url_param 

    def set_url_params(self, url_params_to_set):
        """ Sets URL parameters, { key1: value1, key2: value2 } """
        if not self.interaction:
            logger.error('Setting url_params: no interaction loaded.')
            return None
        for k, v in url_params_to_set.iteritems():
            self.interaction.request.set_url_param([k, v])

    def blend(self):
        """ Makes a request and return the data, it is currently quite ad
        hoc but it works """
        # Testing if an interaction is properly loaded
        if not self.interaction:
            logger.error('Blending: no interaction loaded.')
            return self.make_blender_response(blender_config='error, no interaction loaded')
        # Retries to make a request three times
        request_not_made = True
        i = 0
        _content, _headers = None
        while request_not_made and i < 3:
            try:
                _content, _headers = self.make_request()
                request_not_made = False
            except Exception:
                i += 1
        # Defines the blender_config
        _blender_config = {  
            "server": self.server.name,
            "interaction": self.interaction.name,
            "parameters": [url_param.convert_to_dict() for url_param in self.interaction.request.url_params],
            "request_url": self.auth_manager.current_auth.current_request_url
        }
        # If the request failed
        if request_not_made:
            logger.error("[No reach] Request: {}".format(self.auth_manager.current_auth.current_request_url))
            return self.make_blender_response(blender_config=_blender_config)
        # Check the status of the response
        _successful_interaction = self.check_status(_headers)
        # Loads the content
        _loaded_content = self.load_content(_content)
        if _successful_interaction and _content:
            logger.info("[Success] Request: {}".format(self.auth_manager.current_auth.current_request_url))
        elif _successful_interaction and not _content:
            logger.warning("[Success but empty content] Request: {}".format(
                self.auth_manager.current_auth.current_request_url))
        else:
            logger.warning("[Failure] Request: {}".format(self.auth_manager.current_auth.current_request_url))
        return self.make_blender_response(
                    blender_config=_blender_config,
                    successful_interaction=_successful_interaction,
                    raw_content=_content, 
                    loaded_content=_loaded_content,
                    headers=_headers
                )

    @staticmethod
    def make_blender_response(blender_config, successful_interaction=False, raw_content=None, loaded_content=None,
                              headers=None):
        blender_response = {    
                    "blender_config": blender_config,
                    "successful_interaction": successful_interaction,
                    "timestamp": str(datetime.datetime.now()),
                    "raw_content": raw_content,
                    "loaded_content": loaded_content,
                    "headers": headers
        }
        return blender_response

    def make_request(self):
        """ Called by blend(), it deals with effectively making the
        request """
        # Checking if the policy manager is OK with making a request
        if not self.policy_manager.get_request_permission(self.server):
            sleeping_time = self.policy_manager.get_sleeping_time(self.server)
            if sleeping_time != 0:
                logger.warning("Blender sleeping for: {} seconds".format(sleeping_time))
                time.sleep(sleeping_time)
                self.policy_manager.reset_server_sleep(self.server)
        # Get the URL parameters
        total_url_params = self.interaction.request.get_total_url_params()
        # Ask the auth_manager to make the request
        content, headers = self.auth_manager.make_request(self.server, self.interaction, total_url_params)
        # Signal the request to the policy_manager
        self.policy_manager.signal_server_request(self.server)
        return content, headers
    
    def check_status(self, headers):
        """ Checks the response status and signals problems if needed """
        status = headers['status']
        logger.debug('status: {}, expected status: {}'.format(status, self.interaction.response.expected_status))
        if not status:
            return False
        elif int(status) == int(self.interaction.response.expected_status):
            return True
        elif int(status) == int(self.server.policy.too_many_calls_response_status):
            self.policy_manager.signal_too_many_calls(self.server, headers)
            return False
        else:
            self.policy_manager.signal_wrong_response_status(self.server, status)
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

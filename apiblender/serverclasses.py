import httplib
import urllib
import urlparse
import oauth2 as oauth
import os
import json
from collections import defaultdict

# TODO: All the configuration files and the parameters formats could be
# checked against schemas.

class Server:
    """ A server is the access-point to a service """
    def __init__(self, server_config):
        self.name = server_config["name"]
        self.host = server_config["host"]
        self.port = server_config["port"]
        if server_config["policy"]:
            self.policy = Policy(server_config["policy"])
        else:
            self.policy = None
        self.interactions = [] 
        for interaction in server_config["interactions"]:
            new_interaction = Interaction(interaction)
            self.interactions.append(new_interaction)


class Policy:
    """ The policy parameters """
    def __init__(self, policy_config):
        self.requests_per_period = policy_config["requests_per_period"]
        self.period = policy_config["period"]
        self.too_many_calls_response_status = \
                policy_config["too_many_calls_response_status"]
        self.too_many_calls_waiting_seconds = \
                policy_config["too_many_calls_waiting_seconds"]


class Interaction:
    """ The parameters for a specific interaction with a server  """
    def __init__(self, interaction_config):
        self.name = interaction_config["name"]
        self.request = Request(interaction_config["request"])
        self.response = Response(interaction_config["response"])
        if 'description' in interaction_config.keys():
            self.description = interaction_config["description"]
        else: self.description = None
        self.extractor = None


class Request:
    """ A request is what is sent to a server """
    def __init__(self, request_config):
        self.url_root_path = request_config["url_root_path"]
        self.method = request_config["method"]
        if "raw_content" in request_config.keys():
            self.raw_content = request_config["raw_content"]
        self.url_params = []
        if "url_params" in request_config.keys():
            for url_param in request_config["url_params"]:
                new_url_param = URLParameter(url_param)
                self.url_params.append(new_url_param)

    def set_url_param(self, url_param_to_set):
        for url_param in self.url_params:
            if url_param_to_set[0] == url_param.key:
                url_param.update_url_param(url_param_to_set)
                return
        # Trick to create a new one if needed
        url_param_config = [url_param_to_set[0], 
                            None, 
                            None, 
                            url_param_to_set[1]]
        new_url_param = URLParameter(url_param_config)
        self.url_params.append(new_url_param)

    def get_total_url_params(self):
        total_url_params = {}
        for url_param in self.url_params:
            if url_param.value != None:
                total_url_params.update({url_param.key: url_param.value})
            elif not url_param.optional:
                new_value = raw_input(  '%s is required, please input' \
                                        ' its value: ' % url_param.key )
                param_to_update = [url_param.key, new_value]
                url_param.update_url_param(param_to_update)
                total_url_params.update({url_param.key: url_param.value})
        return total_url_params


class URLParameter:
    """ Parameters of the request can be specified in the URL """
    def __init__(self, url_param):
        self.key = url_param[0]
        self.value_type = url_param[1]
        self.optional = url_param[2]
        self.value = url_param[3]

    def update_url_param(self, url_param_to_set):
        self.key = url_param_to_set[0]
        self.value = url_param_to_set[1]

    def __str__(self):
        return  "\n\t{0:20} {1}".format('Key:', self.key) +\
                "\n\t---" +\
                "\n\t{0:20} {1}".format('Type:', self.value_type) +\
                "\n\t{0:20} {1}".format('Optional:', self.optional) +\
                "\n\t{0:20} {1}".format('Current value:', self.value)

    def convert_to_dict(self):
        return {    'key': self.key,
                    'value_type': self.value_type,
                    'optional': self.optional,
                    'value': self.value             }

class Response:
    """ The response is what is received from the server """
    def __init__(self, response_config):
        if "expected_status" in response_config.keys():
            self.expected_status = response_config["expected_status"]
        else:
            self.expected_status = 200
        if response_config["serialization_format"] in ["JSON", "XML"]:
            self.serialization_format = response_config["serialization_format"]
        else:
            raise Exception

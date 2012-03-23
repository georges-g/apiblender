import httplib
import urllib
import urlparse
import oauth2 as oauth

class Server:

    def __init__(self, server_config):
        #
        # TODO: validation
        #
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

    def __init__(self, policy_config):
        # TODO: validation
        self.requests_per_hour = policy_config["requests_per_hour"]
        self.too_many_calls_response_code = \
                policy_config["too_many_calls_response_code"]
        self.too_many_calls_waiting_seconds = \
                policy_config["too_many_calls_waiting_seconds"]


class Interaction:

    def __init__(self, interaction_config):
        # TODO: validation
        self.name = interaction_config["name"]
        self.description = interaction_config["description"]
        self.request = Request(interaction_config["request"])
        self.response = Response(interaction_config["response"])


class Request:
    
    def __init__(self, request_config):
        # TODO: validation
        self.root_path = request_config["root_path"]
        self.method = request_config["method"]
        if "raw_content" in request_config.keys():
            self.raw_content = request_config["raw_content"]
        self.parameters = []
        if "parameters" in request_config.keys():
            for parameter in request_config["parameters"]:
                new_parameter = Parameter(parameter)
                self.parameters.append(new_parameter)

    def set_parameter(self, parameter_to_set):
        for parameter in self.parameters:
            if parameter_to_set[0] == parameter.key:
                parameter.update_parameter(parameter_to_set)
                return
        # Small trick to create a new one if needed
        parameter_config = [parameter_to_set[0], 
                            None, 
                            None, 
                            parameter_to_set[1]]
        new_parameter = Parameter(parameter_config)
        self.parameters.append(new_parameter)

    def get_total_parameters(self):
        total_parameters = {}
        for parameter in self.parameters:
            if parameter.value != None:
                total_parameters.update({parameter.key: parameter.value})
        return total_parameters


class Parameter:

    def __init__(self, parameter):
        self.key = parameter[0]
        self.value_type = parameter[1]
        self.optional = parameter[2]
        self.value = parameter[3]

    def update_parameter(self, parameter_to_set):
        #TODO: check param
        self.key = parameter_to_set[0]
        self.value = parameter_to_set[1]


class Response:

    def __init__(self, response_config):
        # TODO: validation
        if "expected_status_code" in response_config.keys():
            self.expected_status_code = response_config["expected_status_code"]
        else:
            self.expected_status_code = 200
        if response_config["serialization_format"] in ["JSON", "XML"]:
            self.serialization_format = response_config["serialization_format"]
        else:
            # TODO: manage exception
            raise Exception
        if "integration" in response_config.keys():
            self.extractor = Extractor(response_config["integration"])
        else:
            self.extractor = None


class Extractor:

    def __init__(self, extractor):
        self.extractor = extractor

    def extract(response):
       return response 
        #TODO
#        for k, v in self.extractor.iteritems():
#            if v:
#                try:
#                    value = utils.getFromDict(result,v)
#                    standardContent.update({k: value})
#                except Exception as e:
#                    continue




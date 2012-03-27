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
        self.request = Request(interaction_config["request"])
        self.response = Response(interaction_config["response"])
        if 'description' in interaction_config.keys():
            self.description = interaction_config["description"]
        else: self.description = None


class Request:
    
    def __init__(self, request_config):
        # TODO: validation
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
        # Small trick to create a new one if needed
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

    def __init__(self, url_param):
        self.key = url_param[0]
        self.value_type = url_param[1]
        self.optional = url_param[2]
        self.value = url_param[3]

    def update_url_param(self, url_param_to_set):
        #TODO: check param
        self.key = url_param_to_set[0]
        self.value = url_param_to_set[1]


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




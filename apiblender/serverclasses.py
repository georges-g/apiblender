import httplib
import urllib

class Server:

    def __init__(self, server_config):

        #
        # TODO: validation
        #

        self.name = server_config["name"]
        self.host = server_config["host"]
        self.port = server_config["port"]

        if server_config["authentication"]:
            if server_config["authentication"]["type"] == "simple":
                self.auth = AuthSimple(server_config["authentication"])
        else:
            self.auth = None

        if server_config["policy"]:
            self.policy = Policy(server_config["policy"])
        else:
            self.policy = None

        self.interactions = [] 
        for interaction in server_config["interactions"]:
            new_interaction = Interaction(interaction)
            self.interactions.append(new_interaction)


class Authentication:

    def __init__(self, auth_config):
        self.type_ = auth_config["type"]


class AuthSimple(Authentication):

    def __init__(self, auth_config):

        #
        # TODO: validation
        #

        self.path = auth_config["path"]
        self.parameters = auth_config["parameters"]

    def request_parameters(self, host, port):

        c = httplib.HTTPSConnection(host, port, timeout = 10)
        total_path = "%s?%s" % (self.path,urllib.urlencode(self.parameters))
        c.request('GET', total_path)
        r = c.getresponse()
        http_response = r.read()
        c.close()

        try:
            auth_parameters = dict(http_response.split('='))
        except ValueError as detail:
            print "ERROR, unexpected authentication response: ", detail
            return None
        return auth_parameters

class AuthOauth2(Authentication):

    def __init__(self, auth_config):
        pass



class Policy:
    def __init__(self, policy_config):

        #
        # TODO: validation
        #

        if policy_config:
            self.requests_per_hour = policy_config["requests_per_hour"]
            self.too_many_calls_response_code = \
                    policy_config["too_many_calls_response_code"]
            self.too_many_calls_waiting_time = \
                    policy_config["too_many_calls_waiting_seconds"]


class Interaction:
    def __init__(self, interaction_config):

        #
        # TODO: validation
        #

        self.name = interaction_config["name"]
        self.description = interaction_config["description"]
        self.request = Request(interaction_config["request"])
        self.response = Response(interaction_config["response"])


class Request:
    
    def __init__(self, request_config):

        #
        # TODO: validation
        #

        self.root_path = request_config["root_path"]
        self.method = request_config["method"]

        if "raw_content" in request_config.keys():
            self.raw_content = request_config["raw_content"]

        if "path_constant_parameters" in request_config.keys():
            self.path_constant_parameters = \
                    request_config["path_constant_parameters"]

        self.path_variable_parameters = request_config["path_variable_parameters"]


class Response:

    def __init__(self, response_config):
        #
        # TODO: validation
        #
        if "expected_status_code" in response_config.keys():
            self.expected_status_code = response_config["expected_status_code"]
        else:
            self.expected_status_code = 200
        if response_config["serialization_format"] in ["JSON", "XML"]:
            self.serialization_format = response_config["serialization_format"]
        else:
            #
            # TODO: manage exception
            #
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




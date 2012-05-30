import httplib
import urllib
import urlparse
import oauth2 as oauth
import os
import json
from collections import defaultdict

EXTRACTORS_PATH = 'config/apis/extraction/'

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
        self.load_extractors()

    def load_extractors(self):
        extractors_config_file = "%s%s.json" % (EXTRACTORS_PATH, self.name)
        if os.path.exists(extractors_config_file):
            with open(extractors_config_file, 'r') as config_file:
                extractors_config = json.load(config_file)
                for item in extractors_config:
                    for interaction in self.interactions:
                        if  str(interaction.name) ==\
                            str(item['interaction_name']):
                            interaction.extractor = \
                                Extractor(item['extractor'])
                            break
    

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

    def __str__(self):
        return  "\n\t{0:20} {1}".format('Key:', self.key) +\
                "\n\t---" +\
                "\n\t{0:20} {1}".format('Type:', self.value_type) +\
                "\n\t{0:20} {1}".format('Optional:', self.optional) +\
                "\n\t{0:20} {1}".format('Current value:', self.value)

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


class Extractor:

    def __init__(self, extractor):
        self.str_extractors = extractor
        print self.extract({'results': [\
                {'from_user_id': 123, 'from_user':\
        're', 'to_user_id': 123, 'profile_image_url': 123},\
                {'from_user_id': 123, 'from_user':\
        're', 'to_user_id': 123, 'profile_image_url': 123}]})

    def extract(self, response):
        return response

#    def extract(self, response):
#        _extracted_response = defaultdict(dict)
#        left_keys = []
#        right_keys = []
#        for str_left_keys, str_right_keys in self.str_extractors.iteritems():
#            left_keys = str_left_keys.split('.')
#            right_keys = str_right_keys.split('.')
#            _extracted_sub_response = self.recursive_extract( response,\
#                                                    left_keys, right_keys)
#            # Merging nested dictionaries by nested keys
#            print _extracted_sub_response
#            print _extracted_response
#            for k, v in _extracted_sub_response.iteritems():
#                _extracted_response[k].update(v)
#        return dict(_extracted_response)
#
#    def recursive_extract(self, response, left_keys, right_keys):
#        print "%s: %s" % (left_keys, right_keys)
#        if not left_keys and not right_keys:
#            return None
#        if len(left_keys) > 0:
#            sub_response = response[str(left_keys.pop(0))]
#        else:
#            sub_response = response
#        new_field = right_keys.pop(0)
#        extracted_response = dict()
#        if (type(sub_response) is list): 
#            extracted_response.update({ new_field: list() })
#            for item in sub_response:
#                if right_keys:
#                    extracted_item = self.recursive_extract( item, \
#                       left_keys, right_keys )
#                extracted_response[new_field].append(extracted_item)
#        elif (type(sub_response) is dict) or (len(right_keys) > 0):
#            extracted_response.update({new_field: \
#                    self.recursive_extract( sub_response, 
#                                        left_keys, 
#                                        right_keys)})
#        else:
#            extracted_response = dict()
#            extracted_response.update({new_field: sub_response})
#        return extracted_response
#
#    def flatten(self, item, predicate):
#        #[[predicate, object]]
#        po = list()
#        if type(item) is dict:
#            for key in item.keys():
#                new_predicate = predicate + key + '_'
#                new_item = item[key]
#                sub_po = self.flatten(new_item, new_predicate)
#                po.extend(sub_po)
#        elif type(item) is list:
#            for new_item in item:
#                sub_po = self.flatten(new_item, predicate)
#                po.extend(sub_po)
#        else:
#            po.append([predicate.strip('_'), item])
#        return po

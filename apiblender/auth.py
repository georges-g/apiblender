import os
import json
import time
import urlparse
import httplib
import urllib
import logging
import base64

import oauth2 as oauth

import config

logger = logging.getLogger('apiblender')

#
# Idea: Auth config files could be checked against schemas
# 

class AuthManager:

    def __init__(self):
        self.current_auth = None

    def load_server(self, server):
        """ Loads a server looking at his auth config file """
        # Loads the config file
        auth_config_file = os.path.join(    config.auth_folder_path, 
                                            server.name + '.json' )
        auth_config = {}
        # If no config file, then no authentication
        if not os.path.exists(auth_config_file):
            self.current_auth = AuthNone()
        # Else, pick the right authentication
        else:
            with open(auth_config_file, 'r') as config_file:
                auth_config = json.load(config_file)
            if auth_config['type'] == 'oauth':
                self.current_auth = AuthOauth2(auth_config)
            elif auth_config['type'] == 'access_token':
                self.current_auth = AuthAccessToken(auth_config)
            elif auth_config['type'] == 'access_token_authorization':
                self.current_auth = AuthAccessTokenAuthorization(auth_config)
            elif auth_config['type'] == 'api_key':
                self.current_auth = AuthAPIKey(auth_config)
            else:
                self.current_auth = AuthNone()
        # Change server's port if needed
        if "port" in auth_config.keys():
            server.port = auth_config["port"]
        # Request parameters that will be used for authentication
        self.current_auth.request_parameters(server.host, server.port)
    
    def make_request(self, server, interaction, url_parameters):
        """ Makes a request using the loaded server """
        return self.current_auth.make_request(  server, 
                                                interaction, 
                                                url_parameters )

# Just in case 
class Authentication:
    def __init__(self, auth_config):
        pass


# TODO: The way those classes are organized could be improved, for instance
# bringing together no auth and auth with an API Key.

class AuthNone(Authentication):
    """ The class for services requiring no authentication """
    def __init__(self):
        self.current_request_url = None

    def request_parameters(self, host, port):
        pass

    def make_request(self, server, interaction, url_parameters):
        if server.port==443:
              c = httplib.HTTPSConnection(server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'https'
        else:
              c = httplib.HTTPConnection( server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'http'
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        self.current_request_url = "%s://%s:%s%s" % \
                    (scheme, server.host, server.port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        c.request(interaction.request.method, total_path)
        response = c.getresponse()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        content = response.read()
        c.close()
        return content, headers
 

class AuthAccessToken(Authentication):
    """ The class for services that require an access token """
    def __init__(self, auth_config):
        self.current_request_url = None
        self.path = auth_config["path"]
        self.parameters = auth_config["parameters"]
        self.password = auth_config["password"]
        self.login = auth_config["login"]
        self.method = auth_config["method"]
        if self.method == None:
          self.method="GET"

    def request_parameters(self, host, port):
        c = httplib.HTTPSConnection(host, port, timeout = 10)
        if self.method == "GET":
            total_path = "%s?%s" % (self.path,urllib.urlencode(self.parameters))
            body = None
        else:
            total_path = self.path
            body = urllib.urlencode(self.parameters)
        self.current_request_url = "https://%s:%s%s" % \
                    (host, port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        headers = {}
        if(self.login != None):
          headers["Authorization"] = "Basic "+base64.b64encode(self.login+":"+self.password)
        c.request(self.method, total_path, body, headers)
        r = c.getresponse()
        http_response = r.read()
        try:
            if r.getheader("Content-Type").startswith("application/json"):
                auth_url_parameters = json.loads(http_response)
            else:
                # TODO The '=' is hardcoded, it is a bit dangerous
                auth_url_parameters = dict(http_response.split('='))
        except ValueError as detail:
            logger.error(  "Unexpected authentication response: \n" +
                            str(detail) + "\nCannot use authentication")
        for key in auth_url_parameters:
            # Should not be required for JSON, but Twitter encodes it all
            # the same
            auth_url_parameters[key]=urllib.unquote(auth_url_parameters[key])
        self.auth_url_parameters = auth_url_parameters 
        c.close()

    def make_request(self, server, interaction, url_parameters):
        if server.port==443:
              c = httplib.HTTPSConnection(server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'https'
        else:
              c = httplib.HTTPConnection( server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'http'
        url_parameters.update(self.auth_url_parameters)
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        self.current_request_url = "%s://%s:%s%s" % \
                    (scheme, server.host, server.port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        c.request(interaction.request.method, total_path)
        response = c.getresponse()
        content = response.read()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        c.close()
        return content, headers
 
 
class AuthAccessTokenAuthorization(Authentication):
    """ The class for services that require an access token, that should
    be passed by an Authorization: Bearer field """
    def __init__(self, auth_config):
        self.current_request_url = None
        self.path = auth_config["path"]
        self.parameters = auth_config["parameters"]
        self.password = auth_config["password"]
        self.login = auth_config["login"]
        self.method = auth_config["method"]
        if self.method == None:
          self.method="GET"

    def request_parameters(self, host, port):
        c = httplib.HTTPSConnection(host, port, timeout = 10)
        if self.method == "GET":
            total_path = "%s?%s" % (self.path,urllib.urlencode(self.parameters))
            body = None
        else:
            total_path = self.path
            body = urllib.urlencode(self.parameters)
        self.current_request_url = "https://%s:%s%s" % \
                    (host, port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        headers = {}
        if(self.login != None):
          headers["Authorization"] = "Basic "+base64.b64encode(self.login+":"+self.password)
        c.request(self.method, total_path, body, headers)
        r = c.getresponse()
        http_response = r.read()
        try:
            bearer_parameters = json.loads(http_response)
        except ValueError as detail:
            logger.error(  "Unexpected authentication response: \n" +
                            str(detail) + "\nCannot use authentication")
        self.bearer_parameters = bearer_parameters 
        c.close()

    def make_request(self, server, interaction, url_parameters):
        if server.port==443:
              c = httplib.HTTPSConnection(server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'https'
        else:
              c = httplib.HTTPConnection( server.host, 
                                          server.port,
                                          timeout = 10 )
              scheme = 'http'
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        self.current_request_url = "%s://%s:%s%s" % \
                    (scheme, server.host, server.port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        c.request(interaction.request.method, total_path, None,
            {'Authorization': 'Bearer '+self.bearer_parameters["access_token"]})
        response = c.getresponse()
        content = response.read()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        c.close()
        return content, headers


class AuthOauth2(Authentication):
    """ The class for services requiring oauth2 authentication """

    def __init__(self, auth_config):
        self.current_request_url = None
        self.consumer_key = auth_config["consumer_key"]
        self.consumer_secret = auth_config["consumer_secret"]
        self.request_token_url = auth_config["request_token_url"]
        self.access_token_url = auth_config["access_token_url"]
        self.authorize_url = auth_config["authorize_url"]

    def request_parameters(self, host, port):
        # TODO: port is not used
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        # Getting the request token
        resp, content = client.request(self.request_token_url, "GET")
        request_token = dict(urlparse.parse_qsl(content))
        # Ask confirmation from the user.
        print   "Go to the following link in your browser: \n" + \
                "%s?oauth_token=%s" % ( self.authorize_url, \
                                        request_token['oauth_token']) + "\n"
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        oauth_verifier = raw_input('What is the PIN? ')
        token = oauth.Token(request_token['oauth_token'],
                    request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
        resp, content = client.request(self.access_token_url, "POST")
        self.access_token = dict(urlparse.parse_qsl(content))
        print "Authentication successful"

    def make_request(self, server, interaction, url_parameters):
        url_parameters = urllib.urlencode(url_parameters)
        self.current_request_url = "https://%s:%s%s?%s" % \
            ( server.host, server.port,
              interaction.request.url_root_path, url_parameters )
        token = oauth.Token(    key=self.access_token['oauth_token'], 
                                secret=self.access_token['oauth_token_secret'])
        consumer = oauth.Consumer(  key=self.consumer_key,
                                    secret=self.consumer_secret )
        client = oauth.Client(consumer, token)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        headers, content = client.request( \
            self.current_request_url, \
            method=interaction.request.method,\
        )
        return content, headers


class AuthAPIKey(Authentication):
    """ The class for services requiring an API Key in the URL parameters """

    def __init__(self, auth_config):
        self.current_request_url = None
        self.auth_url_parameters = auth_config["url_parameters"]
        if 'https' in auth_config.keys():
            self.https = auth_config["https"]
        else:
            self.https = false

    def request_parameters(self, host, port):
        pass

    def make_request(self, server, interaction, url_parameters):
        if self.https:
            c = httplib.HTTPSConnection( server.host, 
                                         server.port,
                                         timeout = 10 )
            scheme='https'
        else:
            c = httplib.HTTPConnection( server.host, 
                                        server.port,
                                        timeout = 10 )
            scheme='http'
        url_parameters.update(self.auth_url_parameters)
        total_path = "%s?%s" % ( interaction.request.url_root_path, 
                                 urllib.urlencode(url_parameters) )
        self.current_request_url = "%s://%s:%s%s" % \
                    (scheme, server.host, server.port, total_path)
        logger.info("[In progress] Request: %s" % (self.current_request_url))
        c.request(interaction.request.method, total_path)
        response = c.getresponse()
        content = response.read()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        c.close()
        return content, headers


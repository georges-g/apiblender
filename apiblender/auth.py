import os
import json
import time
import urlparse
import httplib
import urllib
import logging

import oauth2 as oauth

AUTH_PATH = os.path.dirname(__file__) + '/config/apis/auth/'


class AuthManager:

    def __init__(self):
        self.current_auth = None

    def load_server(self, server):
        """ Loads a server looking at his auth config file """
        # Loads the config file
        auth_config_file = "%s%s.json" % (AUTH_PATH, server.name)
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
            elif auth_config['type'] == 'api_key':
                self.current_auth = AuthAPIKey(auth_config)
            else:
                self.current_auth = AuthNone()
        # Requests parameters that will be used for authentication
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
        pass

    def request_parameters(self, host, port):
        pass

    def make_request(self, server, interaction, url_parameters):
        c = httplib.HTTPConnection( server.host, 
                                    server.port,
                                    timeout = 10 )
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        logging.info("Request: %s:%s%s" % \
                    (server.host, server.port, total_path))
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
        # TODO: validation
        self.url = auth_config["url"]
        self.url_parameters = auth_config["url_parameters"]
        if "port" in auth_config.keys():
            self.port = auth_config["port"]
        else:
            self.port = 443

    def request_parameters(self, host):
        c = httplib.HTTPSConnection(host, self.port, timeout = 10)
        total_path = "%s?%s" % (self.url,urllib.urlencode(self.url_parameters))
        c.request('GET', total_path)
        r = c.getresponse()
        http_response = r.read()
        c.close()
        try:
            # TODO The '=' is hardcoded, it is a bit dangerous
            auth_url_parameters = dict(http_response.split('='))
        except ValueError as detail:
            logging.error(  "Unexpected authentication response: \n" +
                            detail + "\nCannot use authentication")
            return
        self.auth_url_parameters = auth_url_parameters 


    def make_request(self, server, interaction, url_parameters):
        c = httplib.HTTPSConnection( server.host, 
                                    self.port,
                                    timeout = 10 )
        url_parameters.update(self.auth_url_parameters)
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        logging.info("Request: %s%s" % (server.host, total_path))
        c.request(interaction.request.method, total_path)
        response = c.getresponse()
        content = response.read()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        c.close()
        return content, headers
 

class AuthOauth2(Authentication):
    """ The class for services requiring oauth2 authentication """

    def __init__(self, auth_config):
        self.consumer_key = auth_config["consumer_key"]
        self.consumer_secret = auth_config["consumer_secret"]
        self.request_token_url = auth_config["request_token_url"]
        self.access_token_url = auth_config["access_token_url"]
        self.authorize_url = auth_config["authorize_url"]
        if "port" in auth_config.keys():
            self.port = auth_config["port"]
        else:
            self.port = 443

    def request_parameters(self, host):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        # Getting the request token
        resp, content = client.request(self.request_token_url, "GET")
        if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])
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
        req_url = "https://%s%s" % (server.host, \
                                    interaction.request.url_root_path)
        token = oauth.Token(    key=self.access_token['oauth_token'], 
                                secret=self.access_token['oauth_token_secret'])
        consumer = oauth.Consumer(  key=self.consumer_key,
                                    secret=self.consumer_secret )
        url_parameters = urllib.urlencode(url_parameters)
        client = oauth.Client(consumer, token)
        headers, content = client.request( \
            req_url, \
            "GET",\
            url_parameters )
        return content, headers


class AuthAPIKey(Authentication):
    """ The class for services requiring an API Key in the URL parameters """

    def __init__(self, auth_config):
        # TODO: validation
        self.auth_url_parameters = auth_config["url_parameters"]
        if 'https' in auth_config.keys():
            self.https = auth_config["https"]
        else:
            self.https = false
        if "port" in auth_config.keys():
            self.port = auth_config["port"]
        else:
            self.port = 443

    def request_parameters(self, host, port):
        pass

    def make_request(self, server, interaction, url_parameters):
        if self.https:
            c = httplib.HTTPSConnection( server.host, 
                                        self.port,
                                        timeout = 10 )
        else:
            c = httplib.HTTPConnection( server.host, 
                                        self.port,
                                        timeout = 10 )
        url_parameters.update(self.auth_url_parameters)
        total_path = "%s?%s" % (    interaction.request.url_root_path, 
                                    urllib.urlencode(url_parameters) )
        logging.info("Request: %s%s" % (server.host, total_path))
        c.request(interaction.request.method, total_path)
        response = c.getresponse()
        content = response.read()
        headers = dict((x,y) for x,y in response.getheaders())
        headers.update({'status': response.status})
        c.close()
        return content, headers


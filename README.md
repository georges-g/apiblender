Description
-------
API Blender allows you to easily interact with multiple Web services.

API Blender has been developed as part of the
ARCOMEM project, <http://arcomem.eu>.

Requirements
------------
* Python 2.7.1+
* Simplegeo oauth2 python implementation:
    1. cd /tmp/
    2. git clone https://github.com/simplegeo/python-oauth2
    3. cd python-oauth2
    4. sudo python setup.py install

Run
---
* (optional) Configure config/general.json
* (optional) If you want to use authentication, configure config/apis/auth
    * rename the empty configuration files removing '-empty', e.g.,
      'facebook-empty.json' -> 'facebook.json'
    * Fill in your parameters
* in Python:
```python
import apiblender

blender = apiblender.Blender()

# A server can be flickr or facebook  
blender.list_servers()
server_name = 'flickr' 
blender.load_server(server_name) 

# An interaction can be a search or retrieving a user's followers
blender.list_interactions()
interaction_name = 'photos_search'
blender.load_interaction(interaction_name)

# URL parameters are used to shape the request
# Serveral parameters can be passed at the same time
blender.list_url_params()
key =   'tags'
value = 'good spirit'
blender.set_url_params({key: value})

# blend() returns shaped data
result = blender.blend()
result['raw_content']
result['prepared_content']
result['headers']
```
    


Then:

``` ./example.py ```

License
-------
Copyright (C) 2011  Georges GOURITEN 

MIT License

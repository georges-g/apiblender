Description
-------
API Blender is a solution to easily interact with multiple Web services.

API Blender has been developed as part of the
ARCOMEM project, <http://arcomem.eu>.

An article on the API Blender has been presented at the WWW12 conference and
is available on 
[Georges Gouriten's website](http://perso.telecom-paristech.fr/~gouriten/).

Requirements
------------
* Python 2.7.1+
* oauth2, cf [the github page](http://github.com/simplegeo/python-oauth2)
* xmltodict, cf [the github page](http://github.com/martinblech/xmltodict)


Installation
---
* sudo python setup.py install
* (optional) Go to the apiblender folder (usually
/usr/local/lib/python2.7/dist-packages/apiblender/), configure the
json.example files in the config directory and rename them into .json files.

The library
---

```python
import apiblender

# Create a blender
blender = apiblender.Blender()

# Load a server
blender.list_servers()
server_name = 'flickr' 
blender.load_server(server_name) 

# Load an interaction 
blender.list_interactions()
interaction_name = 'photos_search'
blender.load_interaction(interaction_name)

# Set the parameters
# Serveral parameters can be passed at the same time
blender.list_url_params()
key =   'tags'
value = 'good spirit'
blender.set_url_params({key: value})

# Execute the request and get the results
result = blender.blend()
result['blender_config']
result['timestamp']
result['raw_content']               # Result content as a string
result['loaded_content']            # Result content as a python dict
result['headers']
result['successful_interaction']    # Boolean
```

Logging
-------

The APIBlender logs everything is a logger called 'apiblender'. You can use
it typically with:

```python
import logging
apiblender_log = logging.getLogger('apiblender')
```

License
-------
Copyright (C) 2011  Georges GOURITEN (georges.gouriten-at-gmail-dot-com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

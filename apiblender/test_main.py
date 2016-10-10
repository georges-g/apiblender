import json
import logging

import main

blender = main.Blender()

apiblender_logger = logging.getLogger('apiblender')
apiblender_logger.setLevel(logging.DEBUG)
apiblender_file_handler = logging.FileHandler('test_main.log')
apiblender_logger.addHandler(apiblender_file_handler)

configs_to_test = [
    # ['google_plus', 'activities_search', 'query', 'hollande'],
    # ['facebook', 'user', 'ids', '7901103'],
    # ['facebook', 'search', 'q', 'hollande'],
    # ['flickr', 'photos_search', 'tags', 'hollande'],
    ['twitter-1.1', 'search', 'q', '@bmw'],
    ['twitter-1.1', 'followers', 'user_id', '813286'],  # Barack Obama
    ['twitter-1.1', 'lists', 'user_id', '813286'],  # Barack Obama
    ['twitter-1.1', 'users_lookup', 'screen_name', 'twitterapi,twitter'],
    # ['twitter-1.1', 'statuses', '813286']
    # ['youtube', 'search', 'q', 'hollande']
]

for config in configs_to_test:
    blender.load_server(config[0])
    blender.load_interaction(config[1])
    blender.set_url_params({config[2]: config[3]})
    res = blender.blend()
    if res['successful_interaction']:
        print "{}, {}: {}".format(config[0], config[1], (res['successful_interaction']))
    else:
        print json.dumps(res)

#!/usr/bin/python
# A very simple example of API Blender

import apiblender
blender = apiblender.Blender()

def get_all_twitter_pages(target_blender):
    target_blender.load_server("twitter-search")
    target_blender.load_interaction("search")
    for p in range(1,15): 
        target_blender.set_parameters({"q": "good spirit", "page": p})
        target_blender.blend()

def just_one_facebook_page(target_blender):
    target_blender.load_server("facebook")
    target_blender.load_interaction("search")
    target_blender.set_parameters({"q": "good spirit"})
    target_blender.blend()
    


just_one_facebook_page(blender)
get_all_twitter_pages(blender)

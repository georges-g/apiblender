#!/usr/bin/python
# A very simple example of API Blender
import main

blender = main.Blender()

def get_all_twitter_pages(target_blender, keyword):
    target_blender.load_server("twitter-search")
    target_blender.load_interaction("search")
    for p in range(1,15): 
        target_blender.set_parameters({"q": keyword, "page": p})
        target_blender.blend()

def just_one_facebook_page(target_blender, keyword):
    target_blender.load_server("facebook")
    target_blender.load_interaction("search")
    target_blender.set_parameters({"q": keyword})
    target_blender.blend()
    
def get_my_followers(target_blender, screen_name):
    target_blender.load_server("twitter-general")
    target_blender.load_interaction("followers")
    target_blender.set_parameters({"screen_name": screen_name})
    target_blender.blend()
    
def get_my_friends(target_blender, screen_name):
    target_blender.load_server("twitter-general")
    target_blender.load_interaction("friends")
    target_blender.set_parameters({"screen_name": screen_name})
    target_blender.blend()

get_my_followers(blender, "twitterapi")
get_my_friends(blender, "twitterapi")
#just_one_facebook_page(blender, "good spirit")
#get_all_twitter_pages(blender, "good spirit")


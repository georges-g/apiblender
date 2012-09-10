#!/usr/bin/python
# Simple examples of the options offered by API Blender
# 
# /!\ Example.py must be moved to a parent directory of apiblender
#
import main

blender = main.Blender()

def get_some_pics_and_comments(target_blender, keyword):
    target_blender.load_server("flickr")
    target_blender.load_interaction("photos_search")
    for p in range(1,2): 
        target_blender.load_interaction("photos_search")
        target_blender.set_url_params({"tags": keyword, "page": p})
        photos_data = target_blender.blend()
        ids = set()
        for photo in photos_data['prepared_content']['photos']['photo']:
            ids.add(photo['id'])
        for _id in ids:
            target_blender.load_interaction("photo_comments")
            target_blender.set_url_params({'photo_id': _id})
            target_blender.blend()

def get_all_youtube_pages(target_blender, keyword):
    target_blender.load_server("youtube")
    target_blender.load_interaction("search")
    for p in range(0,1): 
        target_blender.set_url_params({"q": keyword, "start-index": p*50+1})
        target_blender.blend()

def get_all_twitter_pages(target_blender, keyword):
    target_blender.load_server("twitter-search")
    target_blender.load_interaction("search")
    for p in range(1,2): 
        target_blender.set_url_params({"q": keyword, "page": p})
        target_blender.blend()

def just_one_facebook_page(target_blender, keyword):
    target_blender.load_server("facebook")
    target_blender.load_interaction("search")
    target_blender.set_url_params({"q": keyword})
    target_blender.blend()
    
def get_my_followers(target_blender, screen_name):
    target_blender.load_server("twitter-generic")
    target_blender.load_interaction("followers")
    target_blender.set_url_params({"screen_name": screen_name})
    target_blender.blend()
    
def get_my_friends(target_blender, screen_name):
    target_blender.load_server("twitter-generic")
    target_blender.load_interaction("friends")
    target_blender.set_url_params({"screen_name": screen_name})
    target_blender.blend()

get_all_twitter_pages(blender, "good spirit")
get_all_youtube_pages(blender, "good spirit")
get_some_pics_and_comments(blender, "good spirit")
just_one_facebook_page(blender, "good spirit")
get_my_followers(blender, "twitterapi")
get_my_friends(blender, "twitterapi")


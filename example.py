#!/usr/bin/python
# A very simple example of API Blender

import apiblender
blender = apiblender.Blender()

def get_all_pages(target_blender):
	target_blender.load_server("twitter-search")
	target_blender.load_interaction("search")

	for p in range(1,15): 
		blender.run({"q": "good spirit", "page": p})

get_all_pages(blender)

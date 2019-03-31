#!/usr/bin/python

import re
import random
import requests
import os
import csv
import logging
import sys

from TwitterAPI import TwitterAPI, TwitterOAuth

# Constants
FOLLOW_ID = 25073877

# Basic logging configuration
logging.basicConfig(level=logging.INFO, filename='twitter.log', filemode='a', format='%(asctime)s %(levelname)s : %(message)s')

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	logging.critical("This script requires Python 3")
	raise ValueError ("This script requires Python 3")
	sys.exit()
	
logging.info("Starting stream_monitor.py...")
print("Starting stream_monitor.py...")

logging.info("Loading replacement urls")
replacement_urls = [
	"https://www.python.org",
	"https://www.google.com POWERED BY PYTHON",
	"https://www.youtube.com POWERED BY PYTHON",
	"https://www.dropbox.org POWERED BY PYTHON",
	"https://www.instagram.com POWERED BY PYTHON",
	"https://www.spotify.com POWERED BY PYTHON",
	"https://www.reddit.com POWERED BY PYTHON"
]

#function definitions
def escapeTexString(string, rep): 
	pattern = re.compile("|".join(map(re.escape,rep.keys()))) # Create single pattern object
	new_string = pattern.sub(lambda match: rep[match.group(0)], string.lower())
	#return new_string.encode('utf-8').replace('\n', ' ')
	return new_string
	
def leechGif():
	try:
		logging.debug("Attempting to retrieve image...")
		filename=str(random.randint(1,400)) + '.gif'
		url='http://www.catgifpage.com/gifs/' + filename
		return requests.get(url).content
	except Exception as e:
		logging.critical("Critical error while retrieving image: {}".format(e))
		return None

#Load replacement dictionary into rep
logging.info("Loading cat vocabulary from csv file")
print("Loading cat vocabulary from csv file")
with open("replace.csv") as f:
	rep = dict(filter(None, csv.reader(f)))

logging.info("Loading Twitter API credentials...")
print("Loading Twitter API credentials...")
try:
	o=TwitterOAuth.read_file()
	logging.debug("Retrieving credentials")
	api = TwitterAPI ( 	o.consumer_key,
				o.consumer_secret,
				o.access_token_key,
				o.access_token_secret)
except Exception as e:
	logging.critical("Exception: {}".format(e))

if __name__ == "__main__":	
	print("Begin session\n")
	r = api.request('statuses/filter',{'follow': FOLLOW_ID})
	for item in r:
		if item['user']['id'] == FOLLOW_ID:
			if ('extended_tweet' in item):	
				incoming_tweet = item['extended_tweet']["full_text"]
			else:	
				incoming_tweet = item['text']

			print ("{}, (User ID {}), tweeted: ".format(item['user']["name"],item['user']["id"]))	
			logging.debug(item)

			incoming_tweet = escapeTexString(incoming_tweet, rep) #perform the replacement
			incoming_tweet = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', "" , incoming_tweet)	
			print ('Modified message: {}\n'.format(incoming_tweet))
			logging.info(incoming_tweet)

			if "media" in item["entities"] or "media" in item["extended_tweet"]["entities"]:
				logging.debug("This tweet contains media")
				print('Contains media')
				img = leechGif()
				u = api.request('statuses/update_with_media', {'status': incoming_tweet},{'media': img})
			else:
				u = api.request('statuses/update',{'status': incoming_tweet})

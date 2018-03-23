#!/usr/bin/python

import re, random, codecs
import wget, requests, os
import urllib2
import unicodecsv as csv
from TwitterAPI import TwitterAPI, TwitterOAuth
from time import gmtime, strftime

LOG_LEVEL = 1

#set unicode
import win_unicode_console
win_unicode_console.enable()

#function definitions

def log_entry(msg, LOG_LEVEL):
	t = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
	if LOG_LEVEL > 0:
		f=codecs.open('/home/tb/bot-logs/autotweet.log','a', encoding='utf-8')
		if LOG_LEVEL >= 1:
			f.write((u'{} : {}').format(t, msg))
		f.close()

def escapeTexString(string, rep): 
	pattern = re.compile("|".join(map(re.escape,rep.keys()))) # Create single pattern object (key to simultaneous replacement)
	new_string = pattern.sub(lambda match: rep[match.group(0)], string.lower())
	return new_string.encode('utf-8').replace('\n', ' ')

def leechGif():
	filename=str(random.randint(1,400)) + '.gif'
	url='http://www.catgifpage.com/gifs/' + filename
	r = requests.get (url)

	while r.status_code != 200:
		print ("{} status: {}").format(url, r.status_code)
		filename=str(random.randint(1,400)) + '.gif'
		url='http://www.catgifpage.com/gifs/' + filename
		r = requests.get (url)

	wget.download(url)
	f = open(filename)
	data = f.read()
	f.close()

	os.remove(filename)
	return data

#Load replacement dictionary into rep
with open("/home/tb/replace.csv") as f:
	rep = dict(filter(None, csv.reader(f)))

FOLLOW_ID = '25073877'

o=TwitterOAuth.read_file()
api = TwitterAPI ( 	o.consumer_key,
			o.consumer_secret,
			o.access_token_key,
			o.access_token_secret)

replacement_urls = [
	"https://www.python.org",
	"https://www.google.com POWERED BY PYTHON",
	"https://www.youtube.com POWERED BY PYTHON",
	"https://www.dropbox.org POWERED BY PYTHON",
	"https://www.instagram.com POWERED BY PYTHON",
	"https://www.spotify.com POWERED BY PYTHON",
	"https://www.reddit.com POWERED BY PYTHON"
]

if __name__ == "__main__":	
	log_entry("Begin session\n",LOG_LEVEL)
	print("Begin session\n")
	while True:
		r = api.request('statuses/filter',{'follow': FOLLOW_ID})
		try:
			for item in r:
				try:
					if str(item['user']["id"]) == str(FOLLOW_ID):

						if ('extended_tweet' in item):	
							incoming_tweet = item['extended_tweet']["full_text"]
						else:	
							incoming_tweet = item['text']

						log_entry(incoming_tweet,LOG_LEVEL)
						print ("{}, (User ID {}), tweeted: ").format(item['user']["name"],item['user']["id"])	

						print incoming_tweet
						print ""
							
						incoming_tweet = escapeTexString(incoming_tweet, rep) #perform the replacement
						incoming_tweet = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', "" , incoming_tweet)	
						print ('Modified message: {}\n').format(incoming_tweet)

						if (("media" in item['entities']) or ("media" in item['extended_tweet']["entities"])):
							print('Contains media')
							img = leechGif()
							u = api.request('statuses/update_with_media', {'status': incoming_tweet},{'media': img})
						else:
							u = api.request('statuses/update',{'status': incoming_tweet})
						#print item['text']
				except urllib2.HTTPError as e:
					print ("Exception raised: {}").format(e)
					log_entry(("Exception raised: {}\n").format(e),LOG_LEVEL)
					#continue
		except Exception as ex:
			print("API Timeout Error: {}".format(ex))
			log_entry(("Exception raised: {}\n").format(ex),LOG_LEVEL)

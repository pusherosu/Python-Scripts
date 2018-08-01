#!/usr/bin/python

import praw
import time
import random
from urllib import quote_plus

RATE_LIMIT = 660
USERNAME = "Hooks017"

reddit= praw.Reddit('bot1')
subreddit = reddit.subreddit("hooksplays")

start_time = time.time()

#Load subreddit list from a config file
with open('subreddits.cfg') as f:
	link_text = [line for line in f]

def start_stream(USERNAME):
	for submission in subreddit.stream.submissions():
		if submission.created_utc < start_time:
			continue
		if submission.author.name == USERNAME:
			reply_text = ("It looks like you posted in the wrong subreddit. The content you are looking for can be found [here](https://www.reddit.com/r/{})").format(random.choice(link_text))
			submission.reply(reply_text)
		
if __name__ == "__main__":

	while True:
		try:
			start_stream(USERNAME)
		except praw.exceptions.PRAWException as e:
			print (e)
			time.sleep(RATE_LIMIT)
			start_time = time.time() # Reset the timer to ignore posts made during the rate limit cooldown
			pass

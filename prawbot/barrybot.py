# Barrybot.py
import random
import praw
import time
import logging
import sys

# Definitions
RATE_LIMIT = 660
USERNAME = "Hooks017"
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("hooksplays")
start_time = time.time()

# Basic logging configuration
logging.basicConfig(level=logging.INFO, 
			filename='barry.log', 
			filemode='a', 
			format='%(asctime)s %(levelname)s : %(message)s')

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")
	logging.critical("This script requires Python 3")
	sys.exit()

with open ('barryisms.txt') as f:
	barryisms = [line for line in f]

#print(reddit.config.username)	
	
def start_stream(USERNAME):
	for comment in subreddit.stream.comments():
		normalized_comment = comment.body.lower()
		if comment.created_utc < start_time:
			continue
		if "barry" in normalized_comment and comment.author.name != reddit.config.username:
			logging.info("{} has summoned the Barry!".format(comment.author.name))
			reply_text = (random.choice(barryisms))
			comment.reply(reply_text)

if __name__ == "__main__":
	logging.info("Starting the bot...")
	while True:
		try:
			start_stream(USERNAME)
		except (praw.exceptions.PRAWException , Exception) as e:
			logging.error("Exception: {}. Starting cooldown timer.".format(e))
			time.sleep(RATE_LIMIT)
			start_time = time.time()
			logging.info("Restarting stream...")

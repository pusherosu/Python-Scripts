# Barrybot.py
import random
import praw
import time

# Definitions
RATE_LIMIT = 660
USERNAME = "Hooks017"
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("hooksplays")
start_time = time.time()

with open ('barryisms.txt') as f:
	barryisms = [line for line in f]
	
def start_stream(USERNAME):
	for comment in subreddit.stream.comments():
		normalized_comment = comment.body.lower()
		if comment.created_utc < start_time:
			continue
		if "barry" in normalized_comment:
			print("{}: {} has summoned the Barry!".format(comment.created_utc,comment.author.name))
			reply_text = (random.choice(barryisms))
			comment.reply(reply_text)

if __name__ == "__main__":
	print("{}: Starting the bot...\n".format(time.ctime()))
	while True:
		try:
			start_stream(USERNAME)
		except (praw.exceptions.PRAWException , Exception) as e:
			print("{}: Exception: {}. Starting cooldown timer.\n".format(format(time.ctime(),e)))
			time.sleep(RATE_LIMIT)
			start_time = time.time()
			print("{}: Restarting stream...\n".format(time.ctime()))
			continue
#		except Exception as er:
#			print("{}: Exception: {}. Starting cooldown timer.\n".format(format(time.ctime(),er)))
#			time.sleep(RATE_LIMIT)
#			start_time = time.time()
#			print("{}: Restarting stream...\n".format(time.ctime()))
#			continue	
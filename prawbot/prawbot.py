#/usr/bin/python

import praw
import time
from urllib import quote_plus

reddit= praw.Reddit('bot1')
subreddit = reddit.subreddit("hooksplays")

start_time = time.time()
reply_text = "It looks like you posted in the wrong subreddit. The content you are looking for can be found "
link_text = '[here](https://www.reddit.com/r/grindr)'

reply_text = reply_text + link_text

for submission in subreddit.stream.submissions():
	if submission.created_utc < start_time:
		continue
	if submission.author.name == "Hooks017":
		submission.reply(reply_text)

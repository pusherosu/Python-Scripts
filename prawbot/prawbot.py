#!/usr/bin/python

import praw
import time
import random
from urllib import quote_plus

reddit= praw.Reddit('bot1')
subreddit = reddit.subreddit("hooksplays")

start_time = time.time()

link_text = ('dickpix','askgaybrows','grindr',
	'lgbt','ainbow','transgendercirclejerk',
	'inthecloset','sissyplace')

reply_text = ("It looks like you posted in the wrong subreddit. The content you are looking for can be found [here](https://www.reddit.com/r/{})").format(random.choice(link_text))

for submission in subreddit.stream.submissions():
	if submission.created_utc < start_time:
		continue
	if submission.author.name == "Hooks017":
		submission.reply(reply_text)
		print (submission.author.name)

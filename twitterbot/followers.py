import logging
import sys
from TwitterAPI import TwitterAPI, TwitterOAuth

# Basic logging configuration
logging.basicConfig(level=logging.INFO, filename='twitter.log', filemode='a', format='%(asctime)s %(levelname)s : %(message)s')

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")
	logging.critical("This script requires Python 3")
	sys.exit()
	
logging.info("Starting service...")

# Create an api connection
try:
	logging.debug("Retrieving credentials")
	o=TwitterOAuth.read_file()
	api = TwitterAPI(o.consumer_key,
					o.consumer_secret,
					o.access_token_key,
					o.access_token_secret)
except Exception as e:
	logging.critical("Exception: {}".format(e))
				 
PM = "Thank you for the follow. I hope I can count on your support in 2020. #DevnullforPresident #Devnull2020"
				 
followers = []
friends = []
nCount = 0
uid = 2269728347 # user id of the monitoring account

# Get current list of followers
for id in api.request('followers/ids'):
    followers.append(id)
	
# Get current list of friends. The API defines a friend as
# someone who is following you while you are following them
for id in api.request('friends/ids'):
    friends.append(id)

# Build a list of users the bot does not currently follow and
# give them a return follow
non_follows = [follower for follower in followers if follower not in friends]
for id in non_follows:
	r = api.request('friendships/create', {'user_id': id})
	if r.status_code == 200:
		status = r.json()
		logging.debug("Not currently following {}, but they are following me. Attempting to follow...".format(status['screen_name']))
		friends.append(id)
		
	r = api.request('direct_messages/new', {'user_id': id , 'text': PM})
	logging.debug("Sending PM to user id {}".format(id))
	nCount += 1
logging.info("{} new followers added.".format(nCount))

# Unfollow anyone who has unfollowed us
non_friends = [friend for friend in friends if friend not in followers]
nCount = 0
for id in non_friends:
	r = api.request('friendships/destroy', {'user_id': id})
	if r.status_code == 200:
		status = r.json()
		logging.debug("unfollowed the traitor known as {}...".format(status['screen_name']))
	nCount += 1
logging.info("{} new traitors removed.".format(nCount))
		
STATUS_MSG = "Updated version is online. {} new followers added.".format(nCount)
r = api.request('direct_messages/new', {'user_id': uid , 'text': STATUS_MSG})
logging.info("Shutting down...")

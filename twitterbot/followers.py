#!/usr/bin/python

from TwitterAPI import TwitterAPI, TwitterOAuth

#create an authorization object
o=TwitterOAuth.read_file()
api = TwitterAPI(o.consumer_key,
                 o.consumer_secret,
                 o.access_token_key,
                 o.access_token_secret)
				 
PM = "Thank you for the follow. I hope I can count on your support in 2020. #DevnullforPresident #Devnull2020"
				 
followers = []
nCount = 0
uid = #user id of the monitoring account

for id in api.request('followers/ids'):
    followers.append(id)

friends = []
for id in api.request('friends/ids'):
    friends.append(id)

non_follows = [follower for follower in followers if follower not in friends]

for id in non_follows:
	r = api.request('friendships/create', {'user_id': id})
	if r.status_code == 200:
		status = r.json()
		#print 'Not currently following %s, but they are following me. Attempting to follow...' % status['screen_name']
		
	r = api.request('direct_messages/new', {'user_id': id , 'text': PM})
	print "Sending PM to user id %s" % id
	nCount += 1
	
print "%i new followers added." % nCount
STATUS_MSG = "Updated version is online. %i new followers added." % nCount
r = api.request('direct_messages/new', {'user_id': uid , 'text': STATUS_MSG})

#Uncomment this section to purge the non-followers!
#non_friends = [friend for friend in friends if friend not in followers]
#
#for id in non_friends:
#	r = api.request('friendships/destroy', {'user_id': id})
#	if r.status_code == 200:
#		status = r.json()
#		print 'unfollowed %s' % status['screen_name']

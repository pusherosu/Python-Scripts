#!/usr/bin/python
"""
App.py
This script relies on Twitch's callback functionality. As a result, it will attempt to "call back" to the computer on which
it is hosted. By default, Flask listens on port 5000. As a result, traffic on this port must be forwarded to the host computer.
Please remember that the Flask development server is not considered a secure solution and should not be used in production.
"""

# Imports
import json
import requests
from flask import Flask, request, abort

app = Flask(__name__)

sub = True
url_root = 'https://api.twitch.tv/helix/users?id='
URL="https://api.twitch.tv/helix/webhooks/hub"

# Fill these in with your own information
external_address='http://0.0.0.0:5000' # This is the public IP address given to you by your ISP. This is typically listed on your router's WAN settings. Port must be specified as well
internal_address='0.0.0.0' # This is the IP address of the host computer as provided by your local DHCP server
your_hub_secret='ANYTHINGYOULIKE' # Put your own secret between the quotes

# Load Twitch configuration data from external file
with open ("twitch.json") as data:
	options = json.load(data)

# Subscribed end points
ENDPOINTS=[
	#"https://api.twitch.tv/helix/streams?user_id=83000650", 				# My stream status
	#"https://api.twitch.tv/helix/users/follows?first=1&to_id=83000650", 	# Who follows me
	#"https://api.twitch.tv/helix/users/follows?first=1&from_id=83000650", 	# Whom I follow
	#"https://api.twitch.tv/helix/subscriptions?broadcaster_id=83000650",	# Get my subscribers
	"https://api.twitch.tv/helix/users/follows?first=1&to_id=83000650" 		# Follow events
]

def do_subscriptions(subscription_mode):
	for ENDPOINT in ENDPOINTS:
		payload ={
			'hub.mode':subscription_mode, 
			'hub.topic': ENDPOINT,
			'hub.callback':external_address,
			'hub.lease_seconds':86400, 
			'hub.secret':your_hub_secret
		}

		header = {'Client-ID' : options['appid']}
		r = requests.post(URL, headers=header, data=payload)
    
def request_user_info(user_id):
	header = {'Client-ID' : options['appid']}
	new_url = url_root + user_id
	user_info = requests.get(new_url, headers=header)
	user_info = json.loads(user_info.content.decode("utf-8"))
	return user_info

# Exposed end points
@app.route("/", methods=['GET','POST'])
def hello():
  # Twitch does NOT like developer apps to return status codes other than 200, even if your code fails
	try:
		if request.method =='GET':
			return(request.args.get('hub.challenge'))
		elif request.method == 'POST':
			r = json.loads(request.data.decode("utf-8"))
			if r["data"][0]["from_name"]:
				user_info = request_user_info(str(r["data"][0]["from_id"]))
				# Replace with your desired behaviour 
				print(user_info['data'][0]['profile_image_url'])
				###########################
			return 'OK'
		else:
			return 'OK'
	except:
		return 'OK'

if __name__ == "__main__":
	if sub:
		do_subscriptions('subscribe')
	app.run(host=internal_address)

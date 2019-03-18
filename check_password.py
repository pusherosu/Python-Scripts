#!/usr/bin/python
import requests
import argparse
import sys
import os
import hashlib

parser = argparse.ArgumentParser(description=
								"""Test for password pwnership - 
								This script will query the haveibeenpwned api at 
								https://api.pwnedpasswords.com/
								This script uses a technique known as k-anonymity
								to query the api using only the first 5 characters
								of the user's SHA-1 hashed password. This technique
								ensures that at no point is the full password hash
								ever being transmitted over the wire.
								It's also a little bit saucy.""")
								
parser.add_argument('password', type=str, nargs='+',
                    help='test this password for pwnership using k-anonymity')

args = parser.parse_args()
ENDPOINT="https://api.pwnedpasswords.com/range/"

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")

# Cross-platform system call to clear console
if sys.platform == 'win32':
	os.system('cls')
else:
	os.system('clear')

if __name__ == "__main__":
	hashed_pw = hashlib.sha1(args.password[0].encode('utf-8')).hexdigest()
	
	# Attempt to request the page. Exit if no response
	try:
		print("Sending requests for hashed passwords that start with {}...".format(hashed_pw[:5]))
		r = requests.get(ENDPOINT + hashed_pw[:5]) 
		if r.status_code != 200:
			print("Response not valid. Expected 200, got {} instead.".format(r.status_code))
			sys.exit()
	except Exception as e:
		print ("Error! {}".format(e))
		sys.exit()

	list_of_hashes = r.text.split('\n')
	for h in list_of_hashes:
		if hashed_pw[5:] == h[:35].lower():
			hcount = int(h.split(':')[1].rstrip())
			print("This password has appeared {} unique times across all known breaches".format(hcount))
			
			# Trolling
			if hcount >= 1000:
				print("Are you kidding me? Did you really think this was a good password?")

#!/usr/bin/python

import sys 
import os
import random
import requests
import re
import csv
from bs4 import BeautifulSoup

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")
	
# Constants
FILE_PATH = "./lotto.csv" # The name of the file into which the numbers will be saved
url="https://www.alc.ca/content/alc/en/winning-numbers.html" # live URL. 

# Local url for testing. This will immediately overwrite the live URL.
# Comment this out to capture live data
# To capture test data, place the "test.html" file in the working directory
# and invoke a temporary http server with "python -m http.server" (no quotes)
url="http://127.0.0.1:8000/test.html" 

# An empty dictionary to hold the relevant draw data for later processing 
# (Not strictly required. Possible future functionality.)
draw_data = {} 
#########################################################################

# Witchcraft!
nums = re.compile(r"""(?<=\"winning_numbers\":)(.*)(?=},\"draw_date\")""")
drawDatesData = re.compile(r"""(?<=drawDatesData: \[\[\"/Date\()(.{13})""")

# As of this time, ALC will happily process requests with python headers
# but if a bunch of them start showing up in the server logs, they may choose
# to start refusing them. As a futureproofing step, randomly select a valid
# user-agent to impersonate a normal browser request
user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
]

headers = {'User-Agent': '{}'.format(random.choice(user_agents)).encode("utf-8")}

# Cross-platform system call to clear console
if sys.platform == 'win32':
	os.system('cls')
else:
	os.system('clear')

# Attempt to request the page. Exit if no response
try:
	print("Sending request for 649 numbers from {}. Posing as {}...".format(url,headers))
	r = requests.get(url,headers=headers) 
	if r.status_code != 200:
		print("Response not valid. Expected 200, got {} instead.".format(r.status_code))
		sys.exit()
except Exception as e:
	print ("Error! {}".format(e))
	sys.exit()
	
# Convert the response text to a BS object and parse it for script blocks
# lxml is an xml parser which also handles html. Requires 'pip install lxml'
soup = BeautifulSoup(r.text,'lxml') 
scripts = soup.find_all('script')

for script_block in scripts:
	# The ALC has several draws. We are only interested in the 649
	if 'gameId: "Lotto649"' in str(script_block):

		# Converting the raw string data to a clean list of numbers
		packed_number_list = nums.findall(str(script_block))
		numbers = packed_number_list[0]
		numbers = numbers.replace('"','')
		numbers = [int(item) for item in numbers[1:-1].split(',')]

		# Locate the unix timestamp
		unix_date = drawDatesData.search(str(script_block))
		
		# Converts the result to a dictionary. 
		# (Not strictly required. Possible future functionality.)
		#########################################################
		draw_data["Date"] = unix_date[0]
		draw_data["Numbers"] = numbers
		print ("Results found : {}".format(draw_data))
		#########################################################

if not draw_data:
	print("No Lotto 649 numbers found this week. Exiting...")
	sys.exit()

# Create a new csv file if it does not already exist
# Add latest numbers and corresponding unix time stamp 
# to the database

with open (FILE_PATH , 'a', newline='', encoding='utf8') as f:
	lineWriter = csv.writer(f)
	lineWriter.writerow([unix_date[0],numbers])

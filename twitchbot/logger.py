#!/usr/bin/python

import socket
import json
import datetime
import time
import sqlite3
from sqlite3 import Error

cmd_state = False

# Load configuration data
# config.json contains your oauth, channel info and admin list
with open ("config.json") as data:
	options = json.load(data)

# SQL Functions
def execute_sql(conn,sql):
	try:
		c = conn.cursor()
		c.execute(sql)
		conn.commit()
		return c
	except Error as e:
		print (e)
	return False
	
def initialize_db(db_file):
	""" 	
	Create database connection to the SQLite file
	:param db_file: name of the database file
	:return: Connection object or None
	"""
	# Set up tables if does not exist
	tables = []
	tables.append('''CREATE TABLE IF NOT EXISTS chatlog (
		id INTEGER PRIMARY KEY, 
		message text NOT NULL, 
		channel text NOT NULL, 
		sentts text NOT NULL, 
		userid text NOT NULL,
		badges text NOT NULL,
		displayname text NOT NULL,
		mod text NOT NULL,
		subscriber text NOT NULL,
		usertype text NOT NULL)''')
	conn = sqlite3.connect(db_file)
	c = conn.cursor()	
	
	try:
		for table in tables:
			sql = execute_sql(conn,table)
			print("Adding table to db")
		return conn
	except Error as e:
		print (e)
	return None

def update_log(data,conn):
	"""
	Add entry to chatlog database
	:param data: json object containing data pertaining to the chatter
	:param conn: database object
	:return: sucess or failure status
	"""

	values = (data['message'],
		data['channel'],
		data['tmi-sent-ts'],
		data['user-id'],
		data['@badges'],
		data['display-name'],
		data['mod'],
		data['subscriber'],
		data['user-type']	
	)
	
	sql = '''INSERT INTO chatlog (message,channel,sentts,userid,badges,displayname,mod,subscriber,usertype) VALUES (?,?,?,?,?,?,?,?,?)'''

	c = conn.cursor()
	c.execute(sql,(values))
	conn.commit()

	return True	
	
# Helper functions
def generate_timestamp():
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return st

# Twitch functions
def send(message, sp = None):
	st = generate_timestamp()
	if (sp is None):
		construct = "PRIVMSG #" + str(options['channel'] + " : " + message + "\r\n")
		s.send((construct).encode())
		print ("{}: Message sent : {}".format(st, message))
	else:
		construct = "PRIVMSG #" + str(options['channel'] + " :/me " + message + "\r\n")

def afk():
	construct = "PONG :tmi.twitch.tv\r\n"
	s.send((construct).encode())
	print("{}: PONG!".format(generate_timestamp()))

def init():
	try:
		print ("Attempting to connect to {} on port {}".format(str(options['server']),int(options['port'])))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(300)
		s.connect((str(options['server']),int(options['port'])))

		print ("Sending feature requests")
		s.send(("CAP REQ :twitch.tv/membership\r\n").encode())
		s.send(("CAP REQ :twitch.tv/commands\r\n").encode())
		s.send(("CAP REQ :twitch.tv/tags\r\n").encode())

		print("Sending user and channel info")
		s.send(("PASS " + str(options['oauth'] + "\r\n")).encode())
		s.send(("NICK " + str(options['username'] + "\r\n")).encode())
		s.send(("JOIN #" + str(options['channel'] + "\r\n")).encode())

	except socket.error as e:
		print (("Socket error: {}".format(e)))
		s.close()
		print ("Closed connection.")
	return s

def parse_message(uin):
	if(uin.startswith("@badges")):
		info = {}

		inputSplit = uin.split(" ",1)
		inputTags = inputSplit[0]
		inputOther = inputSplit[1]
		inputMessage = inputSplit[1].split(":")

		#This is a check to stop messages from being sent to chat
		if(":jtv MODE" in uin or "GLOBALUSERSTATE" in uin or "USERSTATE" in uin or "ROOMSTATE" in uin or "JOIN #" in uin or "tmi.twitch.tv 353" in uin or "tmi.twitch.tv 366" in uin):
			info["display-name"] = "twitch"

		elif(uin.startswith("PING")):
			print("Received ping from server. Responding")
			afk()

		#Gets the message sent and the channel from whence it was sent
		elif(len(inputMessage) == 3):
			msgInit = inputMessage[2]
			message = msgInit.split("\r")[0]
			info["message"] = message

			if(message.startswith("ACTION")):
				info["action-message"] = True
			else:
				info["action-message"] = False

			chanInit = inputMessage[1]
			strSplit = chanInit.split(" ")
			chanTear = strSplit[2].split("#")
			channel = chanTear[1]
			info["channel"] = channel

		#splits remaining tags into the dictionary
		tags = inputTags.split(";")
		for i, t in enumerate(tags):
			obj = t.split("=")
			objTitle = obj[0]
			objValue = obj[1]
			info[objTitle] = objValue

			if(i >= len(tags) -1):
				if(info["user-type"] == ""):
					info["user-type"] = "all"
					return info
				else:
					return info

	else:
		info = {}
		inputSplit = uin.split(" ")
		info["message"] = ""
		info["channel"] = ""
		info["sent-ts"] = ""
		info["user-id"] = ""
		info["@badges"] = ""
		info["display-name"] = "twitch"
		info["mod"] = "0"
		info["subscriber"] = "0"
		info["user-type"] = ""

		return info

def parse_command(msg,name):
	global cmd_state
	#return_msg = ""

	# Are commands currently enabled? If disabled, return immediately
	if (cmd_state == False and msg != "!setcommand"):
		return ("Commands are currently disabled")

	# Are we attempting to set the command state? Are we authorized to do so?
	if (msg == "!setcommand" and name in options["admins"]):
		cmd_state = not cmd_state
		print ("Commands Enabled is now set to {}".format(str(cmd_state)))
		return None
	elif (msg == "!setcommand" and name in options["admins"]):
		return ("Invalid command : {}".format(msg))
	elif (msg == "!commandstate"):
		return ("Commands Enabled is now set to {}".format(str(cmd_state)))

	# Custom commands
	elif (msg == "!custom1"):
		# Insert custom code here
		return "{} issued custom command #1".format(name)
	elif (msg == "!custom2"):
		# Insert custom code here
		return "{} issued custom command #2".format(name)
	elif (msg == "!custom3"):
		# Insert custom code here
		return "{} issued custom command #3".format(name)

	else:
		print("{}: Invalid command : {}".format(generate_timestamp(), msg))
		return None		
###############################################################################################

if __name__ == "__main__":
	# Connect to database
	db = initialize_db("twitchlog.db")
	# Connect to twitch over IRC
	s = init()
	print ("Init completed successfully!")
	print("--BEGIN LISTENER--\n")
	send("Mr Stabby is online!")
	
	while s:
		disp = s.recv(1024) 
		disp = disp.decode()

		#########################
		if disp == "PING :tmi.twitch.tv\r\n":
			print ("{}: PING!".format(generate_timestamp()))
			afk()
		#########################
		message = disp.split("\n")
		disp = disp.encode()
		disp = message.pop()

		for line in message:
			response = parse_message(line)
			
			# Does the message contain a command?
			if("message" in response and response['message'].startswith("!")):
				return_message = parse_command(response['message'],response['display-name'])
				if ( return_message != None):
					send (return_message)
			
			# Does the message exist, and if so, does it belong to Twitch, or a real viewer?
			elif("message" in response and response['display-name'] != 'twitch'):
				print("{}: {} said : {}".format(generate_timestamp(), response['display-name'],response['message']))
				update_log(response,db)
			
	s.close()
	print ("{}: Closed connection.".format(generate_timestamp()))

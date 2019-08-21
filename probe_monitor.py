#!/usr/bin/python

import sqlite3
import argparse
import time
import os
from datetime import datetime
from scapy.all import sniff, Dot11

parser = argparse.ArgumentParser()
parser.add_argument('--interface', '-i', default='wlan0', help='Monitor mode enabled interface')
parser.add_argument('--buffer', '-b' , type=int, default=10, help='Buffer size. Hold database transactions until buffer fills. Larger number means less frequent writes. Default is 10')
parser.add_argument('--channel', '-c', type=int, default=-1, help='Specify channel to scan. Default is to channel hop')
args = parser.parse_args()

IGNORE_LIST = set(['00:00:00:00:00:00','01:01:01:01:01:01'])
MAX_TRANSACTIONS = args.buffer
sql_transaction = []

# Initialize channel
if args.channel == -1:
	CURRENT_CHANNEL = 1
else:
	CURRENT_CHANNEL = args.channel

connection = sqlite3.connect('probes.db')
c = connection.cursor()

def create_db():
	c.execute("""CREATE TABLE IF NOT EXISTS access_points (
		essid STRING UNIQUE,
		ssid STRING,
		encryption_type	STRING,
		wpa_seq	BLOB,
		latitude FLOAT,
		longitude FLOAT,
		time STRING,
		rssi TEXT,
		channel	INTEGER);""")

	c.execute("""CREATE TABLE IF NOT EXISTS known_clients (
		client_mac TEXT NOT NULL,
		client_name TEXT,
		comment	TEXT);""")

	c.execute("""CREATE TABLE IF NOT EXISTS probes (
		time STRING,
		bssid STRING,
		essid STRING, 
		client_mac STRING,
		client_name STRING);""")

	c.execute("""CREATE TABLE IF NOT EXISTS vendor_oui (
		mac_address_prefix TEXT NOT NULL UNIQUE,
		vendor TEXT,
		date_added TEXT,
		comment	TEXT,
		PRIMARY KEY(mac_address_prefix));""")

def transaction_bldr(sql):
	global sql_transaction
	sql_transaction.append(sql)
	if len(sql_transaction) >= MAX_TRANSACTIONS:
		print ("\033[95m" + "Updating database" + "\033[0m")
		c.execute('BEGIN TRANSACTION')
		for s in sql_transaction:
			try:
				c.execute(s)
			except Exception as e:
				print("SQL Transaction error " , e)
				pass
		connection.commit()
		sql_transaction = []

def sql_insert(**kwargs):
	try:
		if kwargs["TABLE"] == "probes":
			sql = """INSERT INTO probes(time, bssid, essid, client_mac) 
			SELECT "{}", "{}", "{}", "{}" 
			WHERE NOT EXISTS(SELECT 1 FROM probes WHERE bssid = "{}" AND client_mac = "{}");""".format(
			kwargs["TIME"], 
			kwargs["BSSID"], 
			kwargs["ESSID"], 
			kwargs["CLIENT_MAC"], 
			kwargs["BSSID"], 
			kwargs["CLIENT_MAC"])
		elif kwargs["TABLE"] == "access_points":
			sql = """INSERT INTO access_points(time, essid, ssid, channel, rssi) 
			SELECT "{}", "{}", "{}", "{}", "{}" 
			WHERE NOT EXISTS(SELECT 1 FROM access_points WHERE essid = "{}");""".format(
			kwargs["TIME"], 
			kwargs["CLIENT_MAC"], 
			kwargs["SSID"], 
			kwargs["CHANNEL"], 
			kwargs["SIGNAL_STRENGTH"], 
			kwargs["CLIENT_MAC"])
		else:
			print("Table does not exist!")
			return
		transaction_bldr(sql)
	except Exception as e:
		print('SQL Insertion error', str(e))

def handle_packet(pkt):
	global CURRENT_CHANNEL
	os.popen("iwconfig {} channel {}".format(args.interface,CURRENT_CHANNEL))
	if not pkt.haslayer(Dot11):
		return
	# Handle probe requests. Subtype 4 is a probe request
	if pkt.type == 0 and pkt.subtype == 4:
		curmac = pkt.addr2
		curmac = curmac.upper()
		if curmac not in IGNORE_LIST and pkt.info != "":
			print("\033[95m" + "Device MAC: {} is looking for access point with SSID: {} on channel {}".format(
				curmac, 
				pkt.info, 
				CURRENT_CHANNEL) + "\033[0m")
			if pkt.info:
				kwargs = {
					"TABLE":"probes",
					"TIME":datetime.now(),
					"BSSID":str(pkt.addr1),
					"ESSID":str(pkt.info),
					"CLIENT_MAC":str(curmac)}
				sql_insert(**kwargs)

	# Handle beacon frames. Subtype 8 is beacon
	elif pkt.type == 0 and pkt.subtype == 8:
		signal_strength = -(256-(ord(pkt.notdecoded[-4:-3])))
		curmac = pkt.addr2
		curmac = curmac.upper()
		print("\033[95m" + "Base Station {} is broadcasting SSID {} on channel {}. Signal strength: {} dBm".format(
			curmac, 
			pkt.info, 
			CURRENT_CHANNEL, 
			signal_strength) + "\033[0m")
		kwargs = {
			"TABLE":"access_points",
			"TIME":datetime.now(),
			"CLIENT_MAC":str(curmac),
			"SSID":pkt.info,
			"CHANNEL":CURRENT_CHANNEL,
			"SIGNAL_STRENGTH":signal_strength}
		sql_insert(**kwargs)

	# If channel hopping is enabled (default configuration), move to next channel
	if args.channel == -1:
		CURRENT_CHANNEL = (CURRENT_CHANNEL % 13) + 1

def main():
	print("\033[1m" + "Attempting to set monitor mode on {}".format(args.interface) + "\033[0m")
	try:
		os.popen("ifconfig {} down".format(args.interface))
		os.popen("iwconfig {} mode monitor".format(args.interface))
		os.popen("ifconfig {} up".format(args.interface))
		print("\033[92m" + "SUCCESS!" + "\033[0m")
	except Exception as e:
		print("\033[91m" + "Unable to set monitor mode: ".format(e) + "\033[0m")
	print("\033[1m" + "Beginning monitoring on {}...".format(args.interface) + "\033[0m")
	create_db()
	sniff(iface=args.interface, prn=handle_packet)
	while 1:
		time.sleep(1)

if __name__ == "__main__":
	main()

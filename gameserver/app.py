#!usr/bin/python3

# Libraries
import logging
import datetime
import os
import mysql.connector as mysql
from flask import Flask, request, Response, jsonify

# Flask config
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# Delete old logs and configure logging
if os.path.exists('./app.log'):
	print('Deleting old logs')
	os.remove('./app.log')
	print('Done!')
else:
	print('No log files found')

logging.basicConfig(
	level=logging.DEBUG,
	filename='app.log',
	filemode='a')

# Connect to database
db = mysql.connect(
	host="localhost",
	user="yourusername",
	passwd="yourpassword",
	database="gameserver"
)
cursor = db.cursor()

# Helper functions
# Standard log entries
def log_request(request):
	timestamp = datetime.datetime.now()
	logging.debug(" {} : Request recieved. Full header dump :{}".format(timestamp,dict(request.headers)))
	logging.info("{} : Request recieved.".format(timestamp))

# Load column names into a list
def load_column_names(table_name):
	column_names = []
	cursor.execute("SHOW COLUMNS FROM {};".format(table_name))
	r = cursor.fetchall()
	for row in r:
		column_names.append(row[0])
	return column_names

# End points
@app.route('/',methods=['GET'])
def welcome():
	log_request(request)
	body={'place-holder' : 'Dont taze me bro!'}
	return jsonify({'body' : body}), 501 # STATUS_NOT_IMPLEMENTED

@app.route('/charinfo', methods=['GET'])
def get_charinfo():
	data = {'error-info' : 'Character does not exist'}
	status=204 # Defaults to "NO_CONTENT". This will send an empty (but valid) JSON object if no such character exists
	column_names = load_column_names("character_data")
	character_id = request.args.get('char_id')
	log_request(request)
	cursor.execute("SELECT * FROM character_data WHERE id = {}".format(character_id))
	r = cursor.fetchone()
	if r is not None:
		data = dict(zip(column_names,r))
		status=200
	return jsonify({'body' : data}), status

if __name__ == "__main__":
	logging.info(" {} : Application start. Listening to 0.0.0.0:5000".format(datetime.datetime.now()))
	app.run(host='0.0.0.0',debug=True)

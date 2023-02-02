import win32con
import win32api
import win32file
import datetime
import logging
import sys
import os

# Defines
# log files
SavePath = "D:\\User\\Documents\\venv3.6\\eq_tools\\"
LogPath = SavePath+"eqmonitor.log"

# directory containing the file to be watched. This should be set to your Titanium\\Everquest\\Logs\\ directory
path_to_watch = "F:\\Everquest\\Titanium\\Everquest\\Logs\\"

# look for changes to a log file
# This should be changed to the actual name of the log file. By default p99 character logs should
# be named "eqlog_<CharacterName>_project1999.txt" for blue or "eqlog_<CharacterName>_P1999Green" for green
# I don't play on red, but it should be equally straightforward
file_to_watch = "eqlog_Halfman_P1999Green.txt" 

# Basic logging configuration
logging.basicConfig(level=logging.INFO, filename=LogPath, filemode='a', format='%(asctime)s %(levelname)s : %(message)s')

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	logging.critical("This script requires Python 3")
	raise ValueError ("This script requires Python 3")
	sys.exit()

logging.info("Starting watch_for_xp.py...")
print("Starting watch_for_xp.py. Press Ctrl+Break to exit...")
#FILE_LIST_DIRECTORY = 0x0001
hDir = win32file.CreateFile (
	path_to_watch,
	win32con.GENERIC_READ,
	#FILE_LIST_DIRECTORY,
	win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
	None,
	win32con.OPEN_EXISTING,
	win32con.FILE_FLAG_BACKUP_SEMANTICS,
	None)
	
# Open and read the file we're interested in
a = open(path_to_watch + file_to_watch, "r")
a.read()

def ProcessNewData( newData ):
	if "You gain experience!!" in newData: 
		logging.debug('XP Event detected')
		#<-----Insert custom behaviour here----->
		#<-----End custom behaviour----->
		
if __name__ == "__main__":
	# Wait for new data and call ProcessNewData for each new chunk that's written
	while True:
		# Wait for a change to occur
		results = win32file.ReadDirectoryChangesW (
			hDir,
			1024,
			False,
			win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
			None,
			None)

		# For each change, check to see if it's updating the file we're interested in
		for action, file in results:
				full_filename = os.path.join (path_to_watch, file)
				if file == file_to_watch:
					newText = a.read()
					if newText != "\n":
						ProcessNewData( newText.strip("\n"))

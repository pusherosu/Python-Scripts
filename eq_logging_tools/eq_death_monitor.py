import win32gui
import win32con
import win32ui
import win32file
import datetime
import logging
import sys
import os
from ctypes import windll
from PIL import Image
from TwitterAPI import TwitterAPI, TwitterOAuth

# Defines
WindowName = "EverQuest"
SavePath = "C:\\Pathto\\Screenshot\\Folder\\"
TimeStamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
FilePath = SavePath+TimeStamp+".png"
LogPath = SavePath+"eqmonitor.log"
TWEET_MSG = "Looks like I died again!"

# directory containing the file to be watched. Currently set to "." (Current working directory).
# Titanium client by default will store the logs at C:\Program Files (x86)\Sony\EverQuest\Logs\
# or C:\Users\<your username>\AppData\Local\VirtualStore\Program Files (x86)\Sony\EverQuest\Logs\
path_to_watch = "C:\\Pathto\\Everquest\\Logs\\" 

# look for changes to a file called output.txt. 
# This should be changed to the actual name of the log file. By default p99 character logs should
# be named "eqlog_<CharacterName>_project1999.txt"
file_to_watch = "eqlog_<Charactername>_project1999.txt" 

# Basic logging configuration
logging.basicConfig(level=logging.INFO, filename=LogPath, filemode='a', format='%(asctime)s %(levelname)s : %(message)s')

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	logging.critical("This script requires Python 3")
	raise ValueError ("This script requires Python 3")
	sys.exit()

logging.info("Starting eq_monitor.py...")
print("Starting eq_monitor.py...")
hDir = win32file.CreateFile (
	path_to_watch,
	win32con.GENERIC_READ,
	win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
	None,
	win32con.OPEN_EXISTING,
	win32con.FILE_FLAG_BACKUP_SEMANTICS,
	None)
# Open the file we're interested in
a = open(path_to_watch + file_to_watch, "r")
# Throw away any exising log data
a.read()

# Twitter api credentials are saved to ~\Lib\site-packages\TwitterAPI\credentials.txt 
# the full path will depend on where you installed python. By default 
# c:\users\<username>\appdata\local\python\<pythonversion>\
# To create a twitter api key, sign up at https://developer.twitter.com/

logging.info("Loading Twitter API credentials...")
print("Loading Twitter API credentials...")
try:
	o=TwitterOAuth.read_file()
	logging.debug("Retrieving credentials")
	api = TwitterAPI ( 	o.consumer_key,
				o.consumer_secret,
				o.access_token_key,
				o.access_token_secret)
except Exception as e:
	logging.critical("Exception: {}".format(e))

def capture_window_contents(WindowName):
	# Locate the window and assign it to a device context
	hwnd = win32gui.FindWindow(None, WindowName)
	if not hwnd:
		logging.debug("Window not found! Exiting...")
		raise Exception ("Window not found! Exiting...")

	left, top, right, bot = win32gui.GetClientRect(hwnd)
	w = right - left
	h = bot - top

	hwndDC = win32gui.GetWindowDC(hwnd)
	mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
	
	# Create a compatible save DC and create a bitmap in memory
	saveDC = mfcDC.CreateCompatibleDC()
	saveBitMap = win32ui.CreateBitmap()
	saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
	saveDC.SelectObject(saveBitMap)
	result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

	# Build an image from memory 
	bmpinfo = saveBitMap.GetInfo()
	bmpstr = saveBitMap.GetBitmapBits(True)
	im = Image.frombuffer(
		'RGB',
		(bmpinfo['bmWidth'], bmpinfo['bmHeight']),
		bmpstr, 'raw', 'BGRX', 0, 1)

	# Release memory and device context
	win32gui.DeleteObject(saveBitMap.GetHandle())
	saveDC.DeleteDC()
	mfcDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, hwndDC)

	if result == 1:
		im.save(FilePath)
	else:
		logging.debug("Document could not be saved!")
		raise Exception ("Document could not be saved!")

def ProcessNewData( newData ):
	if "You have been slain" in newData: 
		print("Not again!")
		capture_window_contents(WindowName)
		file = open(FilePath, 'rb')
		data = file.read()
		r = api.request('statuses/update_with_media', {'status': TWEET_MSG},{'media': data})
		logging.debug('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)
		
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

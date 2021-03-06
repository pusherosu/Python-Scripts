import os
import win32file
import win32con
import sys

if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")
	sys.exit()

# directory containing the file to be watched. Currently set to "." (Current working directory).
# Titanium client by default will store the logs at C:\Program Files (x86)\Sony\EverQuest\Logs\
# or C:\Users\<your username>\AppData\Local\VirtualStore\Program Files (x86)\Sony\EverQuest\Logs\
path_to_watch = "." 

# look for changes to a file called output.txt. 
# This should be changed to the actual name of the log file. By default p99 character logs should
# be named "eqlog_<CharacterName>_project1999.txt"
file_to_watch = "output.txt" 

def ProcessNewData( newData ):
	print ("Text added: {}".format(newData))
	#Add desired behaviour here
	
# Set up the bits we'll need for output (Future functionality)
ACTIONS = {
	1 : "Created",
	2 : "Deleted",
	3 : "Updated",
	4 : "Renamed from something",
	5 : "Renamed to something"
}
FILE_LIST_DIRECTORY = 0x0001
hDir = win32file.CreateFile (
	path_to_watch,
	FILE_LIST_DIRECTORY,
	win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
	None,
	win32con.OPEN_EXISTING,
	win32con.FILE_FLAG_BACKUP_SEMANTICS,
	None
)

# Open the file we're interested in
a = open(file_to_watch, "r")

# Throw away any exising log data
a.read()

# Wait for new data and call ProcessNewData for each new chunk that's written
while True:
	# Wait for a change to occur
	results = win32file.ReadDirectoryChangesW (
		hDir,
		1024,
		False,
		win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
		None,
		None
	)

	# For each change, check to see if it's updating the file we're interested in
	for action, file in results:
			full_filename = os.path.join (path_to_watch, file)
			#print (file, ACTIONS.get (action, "Unknown"))
			if file == file_to_watch:
				newText = a.read()
				if newText != "\n":
					ProcessNewData( newText.strip("\n"))
				else:
					print("Nothing but a line terminator here")

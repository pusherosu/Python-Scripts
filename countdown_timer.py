import time
import argparse
from playsound import playsound

parser = argparse.ArgumentParser(description='Countdown timer. Dumps results to file called timer.txt. Time must be greater than 0.')
parser.add_argument('-t', '--time', type=int, default=300, help='Integer value representing the number of seconds')
parser.add_argument('-a', '--alarm', type=bool, nargs='?', const=True, default=False, help='Sound an alarm at 0:00')
args = parser.parse_args()

if args.time <= 0:
	print("Invalid value passed to --time. Time must be greater than 0.")
	parser.print_help()
	exit()

ALARM = 'c:\\path\\to\\alarm.mp3'

def countdown(t):
	while t:
		mins, secs = divmod((t-1), 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		f = open('timer.txt','w')
		f.write(timeformat)
		f.close()
		print(timeformat, end='\r')
		time.sleep(1)
		t -= 1

if __name__ == "__main__":
	print('Countdown running')
	countdown(args.time)
	if args.alarm:
		playsound(ALARM)

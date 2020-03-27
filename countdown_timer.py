import time
seconds = 300 #300 seconds = 5 minutes

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
	countdown(seconds)

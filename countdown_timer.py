import time
seconds = 360

def countdown(t):
	#with open('timer.txt', 'w') as f:
	while t:
		mins, secs = divmod(t, 60)
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

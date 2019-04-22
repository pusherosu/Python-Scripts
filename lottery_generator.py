#!/usr/bin/python3

import random
import json
import datetime
import argparse
import sys

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")

parser = argparse.ArgumentParser(description="Generate test batches of lottery numbers")
parser.add_argument('-r' , help="Number of runs" , type=int , default=1)
parser.add_argument('-b' , help="Number of numbers drawn for each run" , type=int , default=6)
parser.add_argument('-m' , help="Maximum value of each number in each run" , type=int , default=50)
parser.add_argument('-o' , help="Name of the output file", type=str , default="lotteries.json")

list_of_lotteries = []
lottery = {}
numbers = []

def generate_numbers():
	numbers = []
	lottery = {}
	date =str(datetime.datetime.now())
	finished = False
	count = 0

	while not finished:
		new_number = random.randrange(1,args.m)
		if new_number not in numbers:
			numbers.append(new_number) 
			count += 1
		else: pass
			#print("duplicate number {} generated".format(new_number))
		if count == args.b:
			finished = True

	lottery['date'] = date
	lottery['numbers'] = sorted(numbers)
	return lottery

if __name__ == "__main__":

	args = parser.parse_args()
	for i in range(1,args.r+1):
		list_of_lotteries.append(generate_numbers())

	for entry in list_of_lotteries:
		print(entry)

	with open(args.o,"a") as f:
		json.dump(list_of_lotteries,f,indent=4)

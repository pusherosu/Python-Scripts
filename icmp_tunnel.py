import struct
import socket
import sys
from random import randint

# Not running python 3? Pull the ripcord!
if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")

payload = b'Random payload AAAAAAAAAAAAAAAAAAAAAAAAA'
dst_addr = '127.0.0.1' # Replace with destination address

def checksum(data):
	s = 0
	n = len(data) % 2
	for i in range (0, len(data)-n , 2):
		s += data[i] + (data[i+1] << 8)
	if n:
		s += data[i+1]
	while (s >> 16):
		s = (s & 0xFFFF) + (s >> 16)
	s = ~s & 0xFFFF
	return s

def icmp():
	type = 8
	code = 0
	chksum = 0
	id = randint(0,0xFFFF)
	seq = 1
	real_chksum = checksum(struct.pack("!BBHHH40s",type,code,chksum,id,seq,payload))
	icmp_pkt = struct.pack("!BBHHH40s",type,code,socket.htons(real_chksum),id,seq,payload)
	return icmp_pkt

if __name__=="__main__":
	s = socket.socket(socket.AF_INET , socket.SOCK_RAW , socket.IPPROTO_ICMP)
	s.setsockopt(socket.SOL_IP , socket.IP_TTL , 5)
	s.sendto(icmp() , (dst_addr , 0))

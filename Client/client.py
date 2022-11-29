#!/usr/bin/env python
import socket
import struct
import sys
import time

NTP_SERVER = "127.0.0.1"
TIME1970 = 2208988800
def sntp_client():
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data = '\x1b' + 47 * '\0'
    client.sendto( data.encode('utf-8'), ( NTP_SERVER, 9001 ))
    data, address = client.recvfrom( 1024 )
    if data:
        print ('Response received from:', address)
    t = struct.unpack( '!12I', data )[10]
    t -= TIME1970
    print ('\tTime=%s' % time.ctime(t))
    print('hi')


sntp_client()
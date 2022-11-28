import datetime
import socket
import queue
from math import floor
from time import time 



# Codigo inspirado en:
# https://github.com/limifly/ntpserver/blob/master/ntpserver.py

#CONFIG
SERVER_VERSION = 3
SERVER_REFERENCE_CLOCK_ID = 0 # REVISAR
SERVER_TYPE = 'PRIMARY'

# Listen for incoming datagrams
while(True):
    
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = str.decode(bytesAddressPair[0])
    address = bytesAddressPair[1]
    print(message)
    

    LI                  = int(message[0, 1], 2)
    VN                  = message[2, 4]
    mode                = int(message[5, 7], 2)
    stratum             = int(message[8, 15], 2)
    poll                = message[16, 23]
    precision           = message[24, 31]
    rootDelay           = message[32, 63]
    rootDispersion      = message[64, 95]
    referenceIdentifier = message[96, 127]
    referenceTimestamp  = message[128, 191]
    originateTimestamp  = message[192, 255]
    receiveTimestamp    = message[256, 319]
    transmiteTimestamp  = message[320, 383]

#    if(VN not in [1,2,3]):
#        break


    # CREANDO RESPUESTA
    reply = '0'*384

    if (SERVER_TYPE == 'PRIMARY'):
        reply[0,1] = '00'
        reply[8,15] = '00000001'
    else:
        reply[0,1] = '10'
        reply[8,15] = '00000000'
    
    reply[2,4] = VN
    reply[16,23] = poll

    if (mode == 3):
        reply[5,7] = '0100'
    else:
        reply[5,7] = '0010'

    # stratum = ?

    #replay[32,63] = ya estan en cero
    #replay[64,95] = ya estan en cero
    # Reference Clolk identifier ???

    #timestamps
    ServerClock = floor(time())
    ServerClock = format(ServerClock, '032b') + '0'*32

    reply[128,191] = ServerClock 
    reply[192,255] = originateTimestamp
    reply[256,319] = ServerClock
    reply[320,383] = ServerClock
"""
class SNTP:
    TABLE = {
        LI                  : int(message[0, 1], 2),
        VN                  : message[2, 4],
        mode                : int(message[5, 7], 2),
        stratum             : int(message[8, 15], 2),
        poll                : message[16, 23],
        precision           : message[24, 31],
        rootDelay           : message[32, 63],
        rootDispersion      : message[64, 95],
        referenceIdentifier : message[96, 127],
        referenceTimestamp  : message[128, 191],
        originateTimestamp  : message[192, 255],
        receiveTimestamp    : message[256, 319],
        transmiteTimestamp  : message[320, 383],
    }
    
    MODE_TABLE = {
        0: "unspecified",
        1: "symmetric active",
        2: "symmetric passive",
        3: "client",
        4: "server",
        5: "broadcast",
        6: "reserved for NTP control messages",
        7: "reserved for private use",
    }

    STRATUM_TABLE = {
        0: "unspecified",
        1: "primary reference",
    }

    LEAP_TABLE = {
        0: "no warning",
        1: "last minute has 61 seconds",
        2: "last minute has 59 seconds",
        3: "alarm condition (clock not synchronized)",
    }
"""

def main():
    # SERVER
    localIP     = "0.0.0.0"
    localPort   = 8000
    bufferSize  = 1024
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("Link Available")


main()
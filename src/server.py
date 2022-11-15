from bitarray import bitarray
import socket
from math import floor
from time import time 

#CONFIG
SERVER_VERSION = 3
SERVER_REFERENCE_CLOCK_ID = 0 # REVISAR
SERVER_TYPE = 'PRIMARY'

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer       = "Datagram Acepted"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Link Available")

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

    UDPServerSocket.sendto(str.encode(reply), address)

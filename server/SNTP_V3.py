#!/usr/bin/python

import threading
import socket
import struct
import queue
import math
import time
import sys

# Variables Globales
taskQueue = queue.Queue()
stopFlag = False

def decimales(number, n = 32):
    return int(abs(int(number)-number*2**n))

class PAQUETE_SNTP:

    PACKET_FORMAT = "!B B B b 11I"
    
    def __init__(self):
        """Constructor.
        Parametros:
        version      -- NTP version
        mode         -- packet mode (client, server)
        tx_timestamp -- packet transmit timestamp
        """
        self.leap_indicator = 0
        self.version_number = 0
        self.mode = 0
        self.stratum = 0
        self.poll_interval = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = ""
        self.ref_timestamp = 0.0
        self.origin_timestamp = 0
        self.recv_timestamp = 0
        self.transmit_timestamp = 0.0

    def to_data(self):
        """Convierte el paquete SNTP a un buffer que puede ser enviado por un socket.
        Returns:
            buffer que respresnta al paquete SNTP
        Raises:
            SNTPException -- in case of invalid field
        """
        try:
            data = struct.pack(PAQUETE_SNTP.PACKET_FORMAT,
            (self.leap_indicator << 6 | self.version_number << 3 | self.mode), # unsigned integer (02b,03b,03b)
            self.stratum,       # unsigned integer 08b
            self.poll_interval, # unsigned integer 08b
            self.precision,     # signed integer 08b
            int(self.root_delay) << 16 | decimales(self.root_delay),    #unsigned integer 32b
            int(self.root_dispersion) << 16 | decimales(self.root_dispersion, 16), #unsigned integer 32b
            self.ref_id, #32b
            int(self.ref_timestamp), #32b
            decimales(self.ref_timestamp, 32), #32b
            int(self.origin_timestamp), #32b
            decimales(self.origin_timestamp, 32), #32b
            int(self.recv_timestamp), #32b
            decimales(self.recv_timestamp), #32b
            int(self.transmit_timestamp), #32b
            decimales(self.transmit_timestamp, 32)) #32b
        
        except struct.error:
            raise Exception("Campos del Paquete SNTP no es valido.")
            
    
        return data

    def from_data(self, data):
        """Este metodo traduce el paquete SNTP recibido a la clase PAQUETE_SNTP.
        Parameters:
            data -- buffer payload
        Raises:
            NTPException -- in case of invalid packet format
        """
        try:
            unpacked = struct.unpack(PAQUETE_SNTP.PACKET_FORMAT, data[0:struct.calcsize(PAQUETE_SNTP.PACKET_FORMAT)])
        except:
            raise Exception("El Paquete SNTP recibido no es valido.")    
            
        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll_interval      = unpacked[2]
        self.precision          = unpacked[3]
        self.root_delay         = float(unpacked[4])/2**16
        self.root_dispersion    = float(unpacked[5])/2**16
        self.ref_id             = unpacked[6]
        self.ref_timestamp      = _to_time(unpacked[7], unpacked[8])
        self.origin_timestamp   = _to_time(unpacked[9], unpacked[10])
        self.recv_timestamp     = _to_time(unpacked[11], unpacked[12])
        self.transmit_timestamp = _to_time(unpacked[13], unpacked[14])
   
class Receptor(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    # levanta el servicio de escucha 
    def run(self):
        global taskQueue, stopFlag
        # Me mantengo escuchando hasta que la Flag me lo indique.
        while (not stopFlag):
            try:
                data,addr = self.socket.recvfrom(1024)
                recvTimestamp = time.time()
                taskQueue.put((data,addr,recvTimestamp))
            except socket.error:
                print("")       


class Procesador(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):
        global taskQueue,stopFlag
        while (not stopFlag):
            try:
                data,addr,recvTimestamp = taskQueue.get()
                PAQUETE_ENTRADA = PAQUETE_SNTP()
                PAQUETE_ENTRADA.from_data(data)
                PAQUETE_ENTRADA.recv_timestamp = recvTimestamp

                PAQUETE_SALIDA = PAQUETE_SNTP()
                PAQUETE_SALIDA.leap_indicator = 0
                PAQUETE_SALIDA.version_number = PAQUETE_ENTRADA.version_number
                if (PAQUETE_ENTRADA.mode == 3):
                    PAQUETE_SALIDA.mode = 4
                else:
                    PAQUETE_SALIDA.mode = 2
                PAQUETE_SALIDA.stratum = 1
                PAQUETE_SALIDA.poll_interval = PAQUETE_ENTRADA.poll_interval
                PAQUETE_SALIDA.precision = 0
                PAQUETE_SALIDA.root_delay = 0
                PAQUETE_SALIDA.root_dispersion = 0
                PAQUETE_SALIDA.ref_id = ""
                aux = time.time()
                PAQUETE_SALIDA.ref_timestamp = aux
                PAQUETE_SALIDA.transmit_timestamp = aux
                PAQUETE_SALIDA.origin_timestamp = PAQUETE_ENTRADA.origin_timestamp
                PAQUETE_SALIDA.recv_timestamp = PAQUETE_ENTRADA.recv_timestamp

                self.socket.sendto(str.encode(PAQUETE_SALIDA.to_data()),addr)
                print("Enviado desde %s hacia %d".format(addr[0],addr[1]))
            except queue.Empty:
                continue

def main():
    localIP     = "127.0.0.1"
    localPort   = 9001
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("Puerto %d Disponible".format(localPort))

    Prog1 = Receptor(UDPServerSocket)
    Prog1.start()

    Prog2 = Procesador(UDPServerSocket)
    Prog2.start()

    while True:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            print ("Exiting...")
            stopFlag = True
            UDPServerSocket.close()
            print ("Exited")
            break
    return sys.exit()

main()
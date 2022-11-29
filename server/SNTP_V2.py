#!/usr/bin/python

import threading
import socket
import queue
import math
import time
import sys

# Variables Globales
taskQueue = queue.Queue()
stopFlag = False

class PAQUETE_SNTP:

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
        data = ""
        data += format(self.leap_indicator, '02b')
        data += format(self.version_number, '03b')
        data += format(self.mode, '03b')
        data += format(self.stratum, '08b')
        data += format(self.poll_interval, '08b')
        data += format(self.precision, '08b')

        data += format(math.floor(self.root_delay), '16b') + '0'*16 #+ format((self.root_delay%1)*10^16, '')
        data += format(math.floor(self.root_dispersion), '16b') + '0'*16
        # cuidado con ref_id al reves
        data += ''.join(format(ord(i), '04b') for i in self.ref_id)
        data += format(int(self.ref_timestamp), '32b') + '0'*32
        data += format(int(self.origin_timestamp), '32b') + '0'*32
        data += format(int(self.recv_timestamp), '32b') + '0'*32
        data += format(int(self.transmit_timestamp), '32b') + '0'*32
    
        return data

    def from_data(self, data):
        """Este metodo traduce el paquete SNTP recibido a la clase PAQUETE_SNTP.
        Parameters:
            data -- buffer payload
        Raises:
            NTPException -- in case of invalid packet format
        """
        print(data)
        print(len(data))
        print("___________________")
        print(data[0:3])
        self.leap_indicator     = int.from_bytes(data[0:3], 'big')
        print(self.leap_indicator)
        print(type(self.leap_indicator))
        self.version_number     = int(data[2:5], 10)
        self.mode               = int(data[5:8], 10)
        self.stratum            = int(data[8:16], 10)
        self.poll_interval      = int(data[16:24], 10)
        self.precision          = int(data[24:32], 10)
        self.root_delay         = int(data[32:48], 10) # +0.data[47]
        self.root_dispersion    = int(data[64:80], 10) # +0.data[80]
        self.ref_id             = chr(int(data[96:100], 10)) + chr(int(data[100:104], 10)) + chr(int(data[104:108], 10)) + chr(int(data[108:112], 10)) + chr(int(data[112:116], 10)) + chr(int(data[116:120], 10)) + chr(int(data[120:124], 10)) + chr(int(data[124:128], 10))
        self.ref_timestamp      = int(data[128:160], 10) #
        self.origin_timestamp   = int(data[160:224], 10)
        self.recv_timestamp     = int(data[256:288], 10)
        self.transmit_timestamp = int(data[320:352], 10)
   
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
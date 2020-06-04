import socket
import select
import errno # Error codes
import sys

from context import source
from source.global_parameters import global_parameters

EXPECTED_DATA_COUNT = 8

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 2000))

client_socket.setblocking(False) # makes receive non blocking 

while True:
    try:
        data_total = []
        instruction = []
        while True: # Receive messages
            chunk = client_socket.recv(global_parameters['DATA_CHUNK_SIZE'])
            if not len(chunk):
                print("Connection closed by the serve")
                sys.exit()
            
            data = float(chunk.decode('utf-8').strip())
            data_total += [data]

            if len(data_total) == EXPECTED_DATA_COUNT:
                instruction += [data_total]
                data_total = []
            # print(f"Data received: {data}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("Reading error:",str(e))
            sys.exit()
        if len(instruction):
            print("INSTRUCTION:", instruction, "\n\n")
        continue

    except Exception as e:
        print("General error:", str(e))
        sys.exit()
import socket
import select

import cv2

from source import global_parameters
from source.path_planning.frame_handler import FrameHandler
frame_handler = FrameHandler()

HEADER_LENGTH = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows for disconnection from port

server_socket.bind((socket.gethostname(), 2000)) 
server_socket.listen() 

# Wait until PLC and camera connections are established 
print("Connecting to PLC...")
while True:
    PLC_socket, PLC_address = server_socket.accept()
    if PLC_address[0] == global_parameters.PLC_IP:
        break
print(f"Connection established with PLC at {PLC_address}")
print("Connecting to camera...")
while True:
    camera_socket, camera_address = server_socket.accept()
    if camera_address[0] == global_parameters.CAMERA_IP:
        break
print(f"Connection established with camera at {camera_address}")

def send_data(vel_data, start_time):
    to_send = package_data(vel_data, start_time)
    PLC_socket.send(to_send)

sockets_list = [PLC_socket, camera_socket]

# clients = {}

# def receive_data(client_socket:socket.socket):
#     try:
#         message_header = client_socket.recv(HEADER_LENGTH)

#         if not len(message_header):
#             return False

#         message_length = int(message_header.decode("utf-8").strip())
#         return {"header":message_header, "data":client_socket.recv(message_length)}
#     except:
#         return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    
    # Camera Action 
    message = receive_data(notified_socket[1])
    if message is False:
        print(f"FATAL ERROR: Lost connection from {notified_socket}")
        break 
    else:
        user = clients[notified_socket]
        print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

        for client_socket in clients:
            if client_socket != notified_socket:
                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]


while True:
    clientsocket, address = server_socket.accept()
    print(f"Connection from {address} has been established")
    clientsocket.send(bytes(to_send, "utf-8"))
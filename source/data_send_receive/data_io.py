import socket
import select

from .. import global_parameters

HEADER_LENGTH = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows for disconnection from port

server_socket.bind((socket.gethostname(), 2000)) 
server_socket.listen() 

# Wait until PLC connection is established 
print("Connecting to PLC...")
PLC_socket, PLC_address = server_socket.accept()
print("Connection established with PLC.")
print("Connecting to camera...")
camera_socket, camera_address = server_socket.accept()
print("Connection established with camera.")

def package_data(vel_data, start_time):
    # vel_data is a list of velocity values for each actuator 
    print("OG_DATA:", vel_data)
    full_data = ""
    for i in range(0, len(vel_data)):
        for j in range(0, len(vel_data[i])):
            # print(f"{str(round(vel_data[i][j], 5)):<{global_parameters.DATA_CHUNK_SIZE}}")
            full_data += f"{str(round(vel_data[i][j], 5)):<{global_parameters.DATA_CHUNK_SIZE}}"

    encoded_data = full_data.encode('utf-8')

    # for i in range(0, len(t), global_parameters.DATA_CHUNK_SIZE):
    #     print("T",i,t[i:i+global_parameters.DATA_CHUNK_SIZE])

    return encoded_data

def send_data(vel_data, start_time):
    to_send = package_data(vel_data, start_time)
    PLC_socket.send(to_send)

# sockets_list = [server_socket]

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

# while True:
#     read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    
#     for notified_socket in read_sockets:
#         if notified_socket == server_socket:
#             client_socket, client_address = server_socket.accept() 

#             user = receive_data(client_socket)
#             if user is False:
#                 continue 

#             sockets_list.append(client_socket)

#             clients[client_socket] = user

#             print(f"Accepted new conenction from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
#         else:
#             message = receive_data(notified_socket)
#             if message is False:
#                 print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
#                 sockets_list.remove(notified_socket)
#                 del clients[notified_socket]
#                 continue 
#             else:
#                 user = clients[notified_socket]
#                 print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

#                 for client_socket in clients:
#                     if client_socket != notified_socket:
#                         client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

#     for notified_socket in exception_sockets:
#         sockets_list.remove(notified_socket)
#         del clients[notified_socket]


# while True:
#     clientsocket, address = server_socket.accept()
#     print(f"Connection from {address} has been established")
#     clientsocket.send(bytes(to_send, "utf-8"))
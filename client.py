# Adapted from https://github.com/Vishal-shakaya/python_socket/blob/master/server.py

import threading
import socket
import tqdm
import os

alias = input('Choose alias >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 59000
client = connect((host, port))      # connect localhost
print(f"[+] Connecting to {host}:{port}")
print("[+] connected.")



def publish(filename):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # send 4096 bytes each time step
    # get the file size
    filesize = os.path.getsize(filename)
    # send the filename and filesize
    client.send(f"{filename}{SEPARATOR}{filesize}".encode())
    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # sendall to assure transimission in busy networks
            client.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))



def fetch(filename, filesize):
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))


def client_listen():
    pass

def client_recv():
    pass




# global_connection = []
# def Handler(connection):
#     # Do something #
#     connected = True 
#     while connected:
#         data = connection.recv(HEADER)
#         if not data:
#             # print_lock.release()
#             print('bye')
#             break;  
#         print(str(data.decode(FORMAT)))
#         connection.send('message_send'.encode(FORMAT))
#     connection.close()
        
# def Start():
#     # 1. Listen incomming connection: 
#     server.listen() 
#     # 2. Accept all connection :
#     while True:
#         # 3. Create Client Thread :
#         conn, addr = server.accept()
#         global_connection.append(conn)

#         print(f'[CONNECTED]-> {addr}') # print_lock.acquire()
        
#         start_new_thread(ClientHandler, (conn,))

#     # 4. Close the connection :   
#     server.close()
    
# print('****[ SERVER STARTING ]****')
# Start()

# # -> Interface
# # -> Listening
# class Client:
#     def __init__(self):
#         pass

#     def publish(self):
#         '''
#         Send message to signal that the client has this file
#         '''
#         pass

#     def fetch(self):
#         '''
#         Send message to server to find the client that contains the file 
#         '''
#         pass
# This is used to to test server, Mr. Khai please just do your work and do not mind us


import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # Dictionary to store connected clients and their files
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

    def handle_client(self, client_socket, addr):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                command = data.split()
                if command[0] == 'publish':
                    self.publish_file(command[1], command[2], addr[0])

                elif command[0] == 'fetch':
                    self.fetch_file(command[1], client_socket)

                elif command[0] == 'discover':
                    self.discover_files(command[1], client_socket)

                elif command[0] == 'ping':
                    client_socket.send("Pong".encode('utf-8'))

                elif command[0] == 'connect':
                    # Sending the signal to target client to establish the connection
                    clientIP = command[1]
                    target_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    address = (clientIP, 6000)
                    target_client.connect(address)
                    message = 2
                    target_client.send(message.encode('utf-8'))
                    target_client.close() # close socket

            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break

    def publish_file(self, local_name, file_name, client_addr):
        if client_addr not in self.clients:
            self.clients[client_addr] = []

        self.clients[client_addr].append((local_name, file_name))

    def fetch_file(self, file_name, client_socket):
        for client_addr, files in self.clients.items():
            for local_name, stored_file_name in files:
                if stored_file_name == file_name:
                    client_socket.send(f"{client_addr} {local_name}".encode('utf-8'))
                    return

        client_socket.send("File not found".encode('utf-8'))

    def discover_files(self, client_hostname, client_socket):
        if (client_hostname, self.port) in self.clients:
            files = "\n".join([f"{fname} ({lname})" for lname, fname in self.clients[(client_hostname, self.port)]])
            client_socket.send(files.encode('utf-8'))
        else:
            client_socket.send("Host not found".encode('utf-8'))

    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_handler.start()

if __name__ == "__main__":
    server = Server('0.0.0.0', 12345)
    server.start()










# import socket
# import threading

# HEADER = 64 # number of bytes of the message length
# PORT = 5050
# # SEVER = "192.168.100.5" # hardcode IP address of the server
# SEVER = socket.gethostbyname(socket.gethostname())	# Get the IP address of the server
# print(SEVER)
# ADDR = (SEVER, PORT) # tuple of IP address and port number
# FORMAT = 'utf-8'
# DISCONNECT_MESSAGE = "!DISCONNECT"

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
# server.bind(ADDR) # bind the socket to the address

# ADDR_clients = [] # client


# # for multi clients, you can store a list of messages and send each of them to all clients

# def broadcast(clientIP):
#     cast_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     address = (clientIP, 6000)
#     cast_client.connect(address)
#     message = f"New peer {clientIP} has joined the server...\n"
#     cast_client.send(message.encode(FORMAT))
#     cast_client.close() # close socket

# def require(ip):
#     target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     addr = (ip, 6000)
#     target.connect(addr)
#     return target

# def handle_client(conn, addr):
#     print(f"[NEW CONNECTION] {addr} is connected.")
#     conn.send("Joined successfully!".encode(FORMAT))
#     ADDR_clients += str(addr)
#     for i in range(ADDR_clients):
#         broadcast(ADDR_clients[i])
#     connected = True
#     while connected:
#         msg_length = conn.recv(HEADER).decode(FORMAT) # receive the message length from the client (64 is the buffer size) / blocking line of code
#         if msg_length: # if there is a message
#             msg_length = int(msg_length) # convert the message length to integer
#             msg = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client
#             if msg == DISCONNECT_MESSAGE:
#                 connected = False
#             print(f"[{addr}] want to handshake {msg}")
            
#             conn.send("Msg received".encode(FORMAT))

#     conn.close() # close the connection

# def start():
#     server.listen() # start listening for connections / also block lines of code below
#     print(f"[LISTENING] Server is listening on {SEVER} \n")
#     while True:
#         conn, addr = server.accept() # store the connection object (to send the information back) and the client address
#         thread = threading.Thread(target=handle_client, args=(conn, addr)) # create a thread for each client
#         thread.start() # start the thread
#         print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    

# print("[STARTING] Server is starting...")
# start()
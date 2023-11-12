# Adapted from https://github.com/Vishal-shakaya/python_socket/blob/master/server.py


import socket
import threading

class Client:
    def __init__(self, server_host, server_port, client_name):
        self.server_host = server_host
        self.server_port = server_port
        self.client_name = client_name
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_host, server_port))

    def handle_file_request(self, file_name, peer_addr):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect(peer_addr)

            peer_socket.send(f"fetch {file_name}".encode('utf-8'))
            response = peer_socket.recv(1024).decode('utf-8')

            if response == 'File not found':
                print(f"File '{file_name}' not found on the selected peer.")
            else:
                peer_info = response.split()
                peer_host = peer_info[0]
                peer_port = int(peer_info[1])

                self.fetch_file_from_peer(file_name, peer_host, peer_port)

            peer_socket.close()

        except Exception as e:
            print(f"Error handling file request: {e}")

    def fetch_file_from_peer(self, file_name, peer_host, peer_port):
        try:
            download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            download_socket.connect((peer_host, peer_port))

            download_socket.send(f"send {file_name}".encode('utf-8'))
            response = download_socket.recv(1024).decode('utf-8')

            with open(file_name, 'wb') as file:
                while response:
                    file.write(response.encode('utf-8'))
                    response = download_socket.recv(1024).decode('utf-8')

            print(f"File '{file_name}' downloaded successfully.")

            download_socket.close()

        except Exception as e:
            print(f"Error fetching file from peer: {e}")

    def start(self):
        try:
            self.client_socket.send(f"register {self.client_name}".encode('utf-8'))

            response_handler = threading.Thread(target=self.handle_server_responses)
            response_handler.start()

            while True:
                command = input("Enter command: ")
                if command.startswith("fetch"):
                    _, file_name, peer_name = command.split()
                    peer_addr = self.fetch_peer_address(peer_name)
                    self.handle_file_request(file_name, peer_addr)

        except KeyboardInterrupt:
            print("Client closed.")

    def handle_server_responses(self):
        while True:
            data = self.client_socket.recv(1024).decode('utf-8')
            print(data)

    def fetch_peer_address(self, peer_name):
        try:
            self.client_socket.send(f"list".encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            peers = eval(response)
            return peers.get(peer_name, None)

        except Exception as e:
            print(f"Error fetching peer address: {e}")
            return None

if __name__ == "__main__":
    client_name = input("Enter your client name: ")
    client = Client('127.0.0.1', 12345, client_name)
    client.start()

































# import threading
# import socket
# import tqdm
# import os

# import socket
# import os
# import glob
# import time
# import threading
# import tcp_client

# # alias = input('Choose alias >>> ')
# # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # host = "127.0.0.1"
# # port = 59000
# # client = connect((host, port))      # connect localhost
# # print(f"[+] Connecting to {host}:{port}")
# # print("[+] connected.")

# inside = True
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientName=socket.gethostname()
# print("Client name is: " + str(clientName))
# Server = input("Enter IP address of the Server you wish to connect: ") 
# Port = 5000
# server_address = (Server, Port)
# client_ip= socket.gethostbyname(socket.gethostname())
# print("Client IP address is: " + str(client_ip))
# s.sendto(clientName,server_address)
# mmsg,add=s.recvfrom(128)
# print(mmsg)



# def publish(filename):
#     SEPARATOR = "<SEPARATOR>"
#     BUFFER_SIZE = 4096 # send 4096 bytes each time step
#     # get the file size
#     filesize = os.path.getsize(filename)
#     # send the filename and filesize
#     client.send(f"{filename}{SEPARATOR}{filesize}".encode())
#     # start sending the file
#     progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
#     with open(filename, "rb") as f:
#         while True:
#             # read the bytes from the file
#             bytes_read = f.read(BUFFER_SIZE)
#             if not bytes_read:
#                 # file transmitting is done
#                 break
#             # sendall to assure transimission in busy networks
#             client.sendall(bytes_read)
#             # update the progress bar
#             progress.update(len(bytes_read))



# def fetch(filename, filesize):
#     # start receiving the file from the socket
#     # and writing to the file stream
#     progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
#     with open(filename, "wb") as f:
#         while True:
#             # read 1024 bytes from the socket (receive)
#             bytes_read = client_socket.recv(BUFFER_SIZE)
#             if not bytes_read:    
#                 # nothing is received
#                 # file transmitting is done
#                 break
#             # write to the file the bytes we just received
#             f.write(bytes_read)
#             # update the progress bar
#             progress.update(len(bytes_read))


# def request_(opt):
#     if opt == 1:
#         pack_seq = 1
#         success = 0
#         a=glob.glob('*txt')
#         #file1 = ""
#         request = "Inform and update |" + clientName + "|" + client_ip +"\r\n"
#         #print "length of header = " + str(len(request)) + "\n"
#         offset = 128 - len(request)
#         for i in range(len(a)):
#             frag = a[i] + "|" + str(os.path.getsize(a[i]))+ "Bytes\r\n"
#             #print "length of file field = " + str(len(frag)) + "\n"
#             if (offset < len(frag)):
#                 #print "inside if offset"
#                 count = 0
#                 while(success == 0):
#                     if (count == 0):
#                         request = request+"\r\n"+str(pack_seq)
#                     start = time.time()
#                     s.sendto(request,server_address)
#                     #pack_seq += 1
#                     print(request)
#                     try:
#                         ack, add = s.recvfrom(128)
#                         elapsed = (time.time()-start)
#                         print(str(elapsed))
#                         print(ack)
#                         ack_seq_no = _extract_(ack,opt)
#                         #print str(ack_seq_no)
#                         if (ack_seq_no == str(pack_seq)):
#                             #print "inside ack no = pack no"
#                             pack_seq += 1
#                             success = 1
#                         else:
#                             success = 0
#                             count += 1
#                         if (success == 1):
#                             request = "Inform and update |" + clientName + "|" + client_ip +"\r\n"
#                             request += frag
#                             offset = 128 - len(request)
#                     except socket.timeout:
#                                 print("Request timed out")
#                                 success = 0
#                                 count += 1
#                     else:
#                         #print "inside else offset"
#                         request += frag
#                         offset -= len(frag)
						
#         success = 0
#         while(success == 0):
#             request = request+"\r\n"+str(pack_seq)
#             s.sendto(request,server_address)
#             print(request)
#             pack_seq += 1 
					
#             try:
#                 ack, add = s.recvfrom(128)
#                 print(str(ack))
#                 success = 1
#                 ack_seq_no = _extract_(ack,opt)
#             except:
#                 print("Request timed out")
#                 success = 1
#                 success -= 1
#     elif opt == 2:
#         pack_seq = 1
#         qfile=input("Enter the desired file name in  --> ")
#         request = "Query for content |" + clientName + "|" + client_ip +"\r\n"+ qfile + "\r\n"
#         s.sendto(request+"\r\n"+str(pack_seq),server_address)
#         ack, add = s.recvfrom(128)
# 		#print ack
#         m1 = ack.split("\r\n")
#         m3 = m1[0].split("|")
#         if (m3[0] == '200 '):
#             ack_seq_no = _extract_(ack,opt)
#             request_file=input("Do you want to request a file?  (Y/N)? ->")
#             if request_file == 'Y':
#                 tcp_client.main()
#                 #os.system("python tcp-client.py &")
#             else:
#                 print("Thank you for communication !!!")
#     elif opt == 3:
#         pack_seq = 1
#         request = "Exit |" + clientName + "|" + client_ip +"\r\n"
#         s.sendto(request+"\r\n"+str(pack_seq),server_address)
#         ack, add = s.recvfrom(128)
# 		#print ack
#         ack_seq_no = _extract_(ack,opt)
	
#     else: 
#         request = str(opt)
#         s.sendto(request + " |" + "\r\n",server_address)
#         ack, add = s.recvfrom(128)
#         #print ack



# def _extract_(mesg,optn):
# 	m1 = mesg.split("\r\n")
# 	#print m1
# 	seq_no = m1[len(m1)-1]
# 	m3 = m1[0].split("|")
# 	#print str(m3[0])
# 	if optn==3:
# 		print("connection closed successfully")
# 		s.close()
# 	elif len(m1) > 3:
# 		del m1[0]
# 		peer_name = []
# 		del m1[len(m1)-2]
# 		del m1[len(m1)-1]
# 		#print m1
# 		if (m3[0] == '200 '):
# 			print("File is with client(s): ")
# 			for j in range(len(m1)):
# 				peer = m1[j].split("|")
# 				i=peer[1].split(",")
# 				ip=i[0].replace("(","")
# 				print(str(peer[0]) + "having IP: "+ str(ip) + " running on port no.: " + str(Port) + "\n")
# 		#peer_name.append(peer[0])
# 		#for i in range(len(peer)):
# 			#peer = m1[i].split("|")
# 			#peer_name.append(peer[0])
		
# 		#else:
# 			#print str(m3)
# 	return seq_no



# class TCP():
#      pass


########################################################################
# import socket
# import threading

# HEADER = 64 # number of bytes of the message length
# PORT = 5050
# FORMAT = 'utf-8'
# DISCONNECT_MESSAGE = "!DISCONNECT"
# SERVER = "192.168.1.174"
# ADDR = (SERVER, PORT)

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket setup
# client.connect(ADDR) # connect to the server

# CLIENT_SEVER_IP = socket.gethostbyname(socket.gethostname())
# CLIENT_SEVER_ADDR = (CLIENT_SEVER_IP, 5000)
# client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
# client_server.bind(ADDR) # bind the socket to the address



# def handshake():
#     connection = True
#     while connection:
#         opt = str(input(">> "))
#         if opt == 'disconnect':
#             connection = False
#             send(DISCONNECT_MESSAGE) # disconnect from the server
#         else:
#             send(opt)
#             print(client.recv(HEADER).decode(FORMAT))
#             handshake_ip = (opt, 6010)
#             handshake_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket setup
#             handshake_socket.connect(handshake_ip) # connect to the wanted peer
#             print(f"Peer {opt} has handshaked successfully...")
#             msg = str(input(">> "))
#             send(msg)
#             handshake_socket.close()

# def receive(conn, addr):
#     connected = True
#     while connected:
#         msg_length = conn.recv(HEADER).decode(FORMAT) # receive the message length from the client (64 is the buffer size) / blocking line of code
#         if msg_length: # if there is a message
#             msg_length = int(msg_length) # convert the message length to integer
#             msg = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 
#             if msg == DISCONNECT_MESSAGE:
#                 connected = False

#             print(f"[{addr}] {msg}")
#             conn.send("Msg received".encode(FORMAT))

#     conn.close() # close the connection

# def client_listen():
#     client_server.listen()
#     print(f"[LISTENING] CLIENT Server is listening on {CLIENT_SEVER_IP} \n")
#     while True:
#         conn, addr = client_server.accept() # store the connection object (to send the information back) and the client address
#         thread = threading.Thread(target=receive, args=(conn, addr)) # create a thread for each client
#         thread.start() # start the thread
#         print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
#         if threading.active_count() == 0:
#             break



# def send(msg):
#     message = msg.encode(FORMAT) # encode the message
#     msg_length = len(message) # get the message length
#     send_length = str(msg_length).encode(FORMAT) # encode the message length
#     padded_send_length = send_length + b' ' * (HEADER - len(send_length)) # pad the message length
#     client.send(padded_send_length) # send the message length
#     client.send(message) # send the message

# handshake()
############################################################################




### OUTDATED
# def client_listen():
#     pass

# def client_recv():
#     pass




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
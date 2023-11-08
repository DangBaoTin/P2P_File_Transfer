# Adapted from https://github.com/Vishal-shakaya/python_socket/blob/master/server.py

import threading
import socket
import tqdm
import os

import socket
import os
import glob
import time
import threading
import tcp_client

# alias = input('Choose alias >>> ')
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = "127.0.0.1"
# port = 59000
# client = connect((host, port))      # connect localhost
# print(f"[+] Connecting to {host}:{port}")
# print("[+] connected.")

inside = True
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientName=socket.gethostname()
print("Client name is: " + str(clientName))
Server = raw_input("Enter IP address of the Server you wish to connect: ") 
Port = 1218
server_address = (Server, Port)
client_ip= socket.gethostbyname(socket.gethostname())
print("Client IP address is: " + str(client_ip))
s.sendto(clientName,server_address)
mmsg,add=s.recvfrom(128)
print(mmsg)



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


def _formrequest_(opt):
    if opt == 1:
        pack_seq = 1
        success = 0
        a=glob.glob('*txt')
        file1 = ""
        request = "Inform and update |" + clientName + "|" + client_ip +"\r\n"
        #print "length of header = " + str(len(request)) + "\n"
        offset = 128 - len(request)
        for i in range(len(a)):
            frag = a[i] + "|" + str(os.path.getsize(a[i]))+ "Bytes\r\n"
            #print "length of file field = " + str(len(frag)) + "\n"
            if (offset < len(frag)):
                #print "inside if offset"
                count = 0
                while(success == 0):
                    if (count == 0):
                        request = request+"\r\n"+str(pack_seq)
                    start = time.time()
                    s.sendto(request,server_address)
                    #pack_seq += 1
                    print(request)
                    try:
                        ack, add = s.recvfrom(128)
                        elapsed = (time.time()-start)
                        print(str(elapsed))
                        print(ack)
                        ack_seq_no = _extract_(ack,opt)
                        #print str(ack_seq_no)
                        if (ack_seq_no == str(pack_seq)):
                            #print "inside ack no = pack no"
                            pack_seq += 1
                            success = 1
                        else:
                            success = 0
                            count += 1
                        if (success == 1):
                            request = "Inform and update |" + clientName + "|" + client_ip +"\r\n"
                            request += frag
                            offset = 128 - len(request)
                    except socket.timeout:
                                print("Request timed out")
                                success = 0
                                count += 1
                    else:
                        #print "inside else offset"
                        request += frag
                        offset -= len(frag)
						
        success = 0
        while(success == 0):
            request = request+"\r\n"+str(pack_seq)
            s.sendto(request,server_address)
            print(request)
            pack_seq += 1 
					
            try:
                ack, add = s.recvfrom(128)
                print(str(ack))
                success = 1
                ack_seq_no = _extract_(ack,opt)
            except:
                print("Request timed out")
                success = 1
                success -= 1
    elif opt == 2:
        pack_seq = 1
        qfile=input("Enter the desired file name in  --> ")
        request = "Query for content |" + clientName + "|" + client_ip +"\r\n"+ qfile + "\r\n"
        s.sendto(request+"\r\n"+str(pack_seq),server_address)
        ack, add = s.recvfrom(128)
		#print ack
        m1 = ack.split("\r\n")
        m3 = m1[0].split("|")
        if (m3[0] == '200 '):
            ack_seq_no = _extract_(ack,opt)
            request_file=input("Do you want to request a file?  (Y/N)? ->")
            if request_file == 'Y':
                tcp_client.main()
                #os.system("python tcp-client.py &")
            else:
                print("Thank you for communication !!!")
    elif opt == 3:
        pack_seq = 1
        request = "Exit |" + clientName + "|" + client_ip +"\r\n"
        s.sendto(request+"\r\n"+str(pack_seq),server_address)
        ack, add = s.recvfrom(128)
		#print ack
        ack_seq_no = _extract_(ack,opt)
	
    else: 
        request = str(opt)
        s.sendto(request + " |" + "\r\n",server_address)
        ack, add = s.recvfrom(128)
        #print ack



def _extract_(mesg,optn):
	m1 = mesg.split("\r\n")
	#print m1
	seq_no = m1[len(m1)-1]
	m3 = m1[0].split("|")
	#print str(m3[0])
	if optn==3:
		print("connection closed successfully")
		s.close()
	elif len(m1) > 3:
		del m1[0]
		peer_name = []
		del m1[len(m1)-2]
		del m1[len(m1)-1]
		#print m1
		if (m3[0] == '200 '):
			print("File is with client(s): ")
			for j in range(len(m1)):
				peer = m1[j].split("|")
				i=peer[1].split(",")
				ip=i[0].replace("(","")
				print(str(peer[0]) + "having IP: "+ str(ip) + " running on port no.: " + str(Port) + "\n")
		#peer_name.append(peer[0])
		#for i in range(len(peer)):
			#peer = m1[i].split("|")
			#peer_name.append(peer[0])
		
		#else:
			#print str(m3)
	return seq_no



class TCP():
     pass

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
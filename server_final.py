import socket
import threading
import os
import signal

HEADER = 64 # number of bytes of the message length
PORT = 5050
# SEVER = "192.168.100.5" # hardcode IP address of the server
SEVER = socket.gethostbyname(socket.gethostname())	# Get the IP address of the server
ADDR = (SEVER, PORT) # tuple of IP address and port number
FORMAT = 'utf-8'
BUFFER_SIZE = 4096 # send 4096 bytes each time step


# DEFINE SOME GLOBAL VARIABLES
listManagedFiles = dict() # list of files that the server manages
client_pool = dict() # list of information of client
numOfClients = 0 # number of clients that the server knows
completion_event = threading.Event()

class Server:
    def __init__(self):
        # create a socket to listen to the client   
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
        self.server.bind(ADDR) # bind the socket to the address

        self.lock = threading.Lock()
        self.threads = []

    def start(self):
        self.server.listen() # start listening for connections / also block lines of code below
        print(f"[LISTENING] Server is listening on {SEVER} \n")

        mainThread = threading.Thread(target=self.handle_server_command)
        mainThread.start()
        with self.lock:
            self.threads.append(mainThread)
        
        while True:
            try:
                conn, addr = self.server.accept()
            except:
                exit()
            global numOfClients
            numOfClients += 1 # increase the number of clients
            clientThread = threading.Thread(target=self.handle_client, args=(conn, addr)) # create a thread for each client
            clientThread.start() # start the thread
            with self.lock:
                self.threads.append(clientThread)

            # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def sendMessage(self, conn, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        padded_send_length = send_length + b' ' * (HEADER - len(send_length))
        conn.send(padded_send_length)
        conn.send(message)

    def receiveMessage(self, conn):
        message = ""
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            message = conn.recv(msg_length).decode(FORMAT)
        return message

    def acknowledgeFiles(self, conn, hostname):
        global listManagedFiles;

        oldFilename = self.receiveMessage(conn)
        newFilename = self.receiveMessage(conn)  

        # ADD THE FILE TO THE LIST OF MANAGED FILES
        with self.lock:
            if newFilename not in listManagedFiles:
                listManagedFiles[newFilename] = [(hostname, oldFilename)]
            else:
                if (hostname, oldFilename) not in listManagedFiles[newFilename]:
                    listManagedFiles[newFilename].append((hostname, oldFilename))
                else: # HANDLE THE CASE THE FILE IS ALREADY IN THE SERVER
                    print(f"The file {oldFilename} is already in the server !")

        with self.lock:
        # Add to the client repository
            if oldFilename not in client_pool[hostname]['fname']:
                client_pool[hostname]['fname'].append(oldFilename)
        
    def updateFileListWhenClientDisconnect(self, conn, hostname):
        global listManagedFiles
        listManagedFiles_copy = listManagedFiles.copy()
        # delete the file in listfiles
        for key in listManagedFiles_copy:
            for i in range(len(listManagedFiles_copy[key])):
                if listManagedFiles_copy[key][i][0] == hostname:
                    with self.lock:
                        listManagedFiles[key].pop(i)
                    break
            with self.lock:
                if len(listManagedFiles[key]) == 0:
                    del listManagedFiles[key]
                    break
        # delete that hostname
        with self.lock: 
            del client_pool[hostname]
        
    def handleFetchFile(self, conn):
        global listManagedFiles
        filename = self.receiveMessage(conn)
        hostname_0 = self.receiveMessage(conn)
        # HANDLE THE FILE NOT FOUND CASE
        if filename not in listManagedFiles:
            self.sendMessage(conn, "File not found !")
            return
        elif len(listManagedFiles[filename]) == 1:
            for element in listManagedFiles[filename]:
                if element[0] == hostname_0:
                    self.sendMessage(conn, "No other hostname has that file !")
                    return
        self.sendMessage(conn, "Here are the list users have that file !")
    

        listUser = "-".join(str(element) for element in listManagedFiles[filename] if element[0] != hostname_0)
        # SEND THE LIST OF USERS HAVE THAT FILE
        # print(listUser)
        self.sendMessage(conn, listUser)
        ## RECEIVE THE HOSTNAME CHOSEN FROM CLIENT
        hostname = self.receiveMessage(conn)
        self.sendMessage(conn, client_pool[hostname]['ip'])
        self.sendMessage(conn, client_pool[hostname]['port_p2p'])

        # FIND THE REAL FILENAME
        for element in listManagedFiles[filename]:
            if element[0] == hostname:
                realFilename = element[1]
                break
        
        # RECEIVE THE STATUS
        status = self.receiveMessage(conn)

        # UPDATE THE LIST OF MANAGED FILES
        if status == "success":
            if (hostname_0, realFilename) not in listManagedFiles[filename]:
                with self.lock:
                    listManagedFiles[filename].append((hostname_0, realFilename))
            client_pool[hostname_0]['fname'].append(realFilename)

    def handle_client(self, conn, addr):
        # print(f"[NEW CONNECTION] {addr} is connected.") # confirm the connection
        global numOfClients
        global client_pool
        connect = True
        # HANDLING HOSTNAME #
        while True:
            hostname = self.receiveMessage(conn)
            if hostname not in client_pool:
                self.sendMessage(conn, "Hostname registered successfully !")
                break
            else: # HANDLING THE CASE THE HOSTNAME ALREADY EXIST
                self.sendMessage(conn, "The hostname already exist !")
        port_p2p = self.receiveMessage(conn)
        port_client_listen = self.receiveMessage(conn)

        # UPDATE INFORMATION IN THE CLIENT POOL
        with self.lock:
            client_pool[hostname] = {
                "ip": addr[0],
                "port_connected": addr[1],
                "port_p2p": port_p2p,
                "port_client": port_client_listen,
                "fname": []
            }


        while connect:
            # receive the command
            command = self.receiveMessage(conn)
            
            # hadle the command
            if command == "publish":
                self.acknowledgeFiles(conn, hostname)
            elif command == "fetch":
                self.handleFetchFile(conn)
            elif command == "disconnect":
                self.updateFileListWhenClientDisconnect(conn, hostname)
                # print(f"{hostname} is disconnected")
                # print(listManagedFiles)
                conn.close()
                connect = False
                numOfClients -= 1
    
        if numOfClients == 0:
            print("No clients connected !")
            print("Server is shutting down...")
            self.exit()
    
    def handle_server_command(self):
        global completion_event
        command = input("Enter the command : ")
        while command != "disconnect":
            command = command.split()
            try:
                if command[0] == "ping":
                    if command[1] not in client_pool:
                        print("The hostname does not exist !")
                        command = input("Enter the command: ")
                        continue
                    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # with self.lock:
                    socket_client.connect((client_pool[command[1]]['ip'], int(client_pool[command[1]]['port_client'])))
                    self.ping(socket_client, completion_event)
                    socket_client.close()
                    completion_event.wait()
                    
                elif command[0] == "discover":
                    if command[1] not in client_pool:
                        print("The hostname does not exist !")
                        command = input("Enter the command: ")
                        continue
                    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # with self.lock:
                    socket_client.connect((client_pool[command[1]]['ip'], int(client_pool[command[1]]['port_client'])))
                    self.dicoverHostname(socket_client, command[1], completion_event)
                    socket_client.close()
                    completion_event.wait()

                elif command[0] == "disconnect":
                    exit()
                else :
                    print("Invalid command !")
            except IndexError:
                print("Invalid command !")


            command = input("Enter the command : ")
            completion_event.clear()
       
    def ping(self, conn, event):
        self.sendMessage(conn, "ping")
        message = self.receiveMessage(conn)
        if message == "pong":
            print("Pong !")
            event.set()
            return
        else:
            event.set()
            return
    
    def dicoverHostname(self, conn, hostname , event):
        # self.sendMessage(conn, "discover")
        #TODO : check lại xem trả ra cái list file của server giữ hay list file trong máy
        # hostname = self.receiveMessage(conn)
        hostname = client_pool[hostname]['fname']
        print(f"All the files of the client is {hostname}")
        event.set()
        return

    def exit(self):
        self.server.close()
        os.kill(os.getpid(), signal.SIGINT)
    

if __name__ == "__main__":
    print("[STARTING] Server is starting... \n")
    server = Server()
    server.start()
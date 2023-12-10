import socket
import threading

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

class Server:
    def __init__(self):
        # create a socket to listen to the client   
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
        self.server.bind(ADDR) # bind the socket to the address

    def start(self):
        self.server.listen() # start listening for connections / also block lines of code below
        print(f"[LISTENING] Server is listening on {SEVER} \n")
        while True:
            conn, addr = self.server.accept() # store the connection object (to send the information back) and the client address
            global numOfClients
            numOfClients += 1 # increase the number of clients
            thread = threading.Thread(target=self.handle_client, args=(conn, addr)) # create a thread for each client
            thread.start() # start the thread
            thread2 = threading.Thread(target=self.connectToClient)
            thread2.start()
            # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} is connected.") # confirm the connection
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
        print(f"Port to client: {port_client_listen}")

        # UPDATE INFORMATION IN THE CLIENT POOL
        client_pool[hostname] = {
            "ip": addr[0],
            "port_connected": addr[1],
            "port_p2p": port_p2p,
            "port_client": port_client_listen,
            "fname": []
        }
        # print(client_pool)
        # thread_connect_client = threading.Thread(target=self.connectToClient)
        # thread_connect_client.start()
        # TODO: handle a thread to connect to te client
        # self.connectToClient(int(port_client_listen))


        while connect:
            # receive the command
            command = self.receiveMessage(conn)
            # print(f"{addr} sent {command}")
            # address = addr # may be need to change to addr[0] for the real IP address
            
            # hadle the command
            if command == "publish":
                self.acknowledgeFiles(conn, hostname)
            elif command == "fetch":
                self.handleFetchFile(conn)
            elif command == "disconnect":
                self.updateFileListWhenClientDisconnect(conn, hostname)
                print(f"{hostname} is disconnected")
                print(listManagedFiles)
                conn.close()
                connect = False
                numOfClients -= 1
    
        # if numOfClients == 0:
        #     print("No clients connected !")
        #     print("Server is shutting down...")
        # server.close()
        # exit()
    
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
        if newFilename not in listManagedFiles:
            listManagedFiles[newFilename] = [(hostname, oldFilename)]
        else:
            if (hostname, oldFilename) not in listManagedFiles[newFilename]:
                listManagedFiles[newFilename].append((hostname, oldFilename))
            else: # HANDLE THE CASE THE FILE IS ALREADY IN THE SERVER
                print(f"The file {oldFilename} is already in the server !")

        # Add to the client repository
        if oldFilename not in client_pool[hostname]['fname']:
            client_pool[hostname]['fname'].append(oldFilename)
        
        # print(client_pool)
        # print(listManagedFiles)

    def updateFileListWhenClientDisconnect(self, conn, hostname):
        global listManagedFiles
        listManagedFiles_copy = listManagedFiles.copy()
    
        for key in listManagedFiles_copy:
            for i in range(len(listManagedFiles_copy[key])):
                if listManagedFiles_copy[key][i][0] == hostname:
                    listManagedFiles[key].pop(i)
                    break
            if len(listManagedFiles[key]) == 0:
                del listManagedFiles[key]
                break
    
    def handleFetchFile(self, conn):
        filename = self.receiveMessage(conn)

        # HANDLE THE FILE NOT FOUND CASE
        if filename not in listManagedFiles:
            # print("File not found !")
            self.sendMessage(conn, "File not found !")
            return
        else:
            self.sendMessage(conn, "Here are the list users have that file !")
    
        # print(listManagedFiles[filename])
        listUser = "-".join(str(element) for element in listManagedFiles[filename])
        # SEND THE LIST OF USERS HAVE THAT FILE
        # print(listUser)
        self.sendMessage(conn, listUser)
        ## RECEIVE THE HOSTNAME FROM CLIENT
        hostname = self.receiveMessage(conn)
        self.sendMessage(conn, client_pool[hostname]['ip'])
        self.sendMessage(conn, client_pool[hostname]['port_p2p'])

    def connectToClient(self):
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command = input("Enter the command: ")
        while command != "disconnect":
            command = command.split()
            if command[0] == "ping":
                socket_client.connect((client_pool[command[1]]['ip'], int(client_pool[command[1]]['port_client'])))
                self.ping(socket_client)
            elif command[0] == "discover":
                socket_client.connect((client_pool[command[1]]['ip'], int(client_pool[command[1]]['port_client'])))
                self.dicoverHostname(socket_client)
            command = input("Enter the command: ")
    
    def ping(self, conn):
        self.sendMessage(conn, "ping")
        message = self.receiveMessage(conn)
        if message == "pong":
            print("The client is alive !")
            return True
        else:
            return False
    
    def dicoverHostname(self, conn):
        self.sendMessage(conn, "discover")
        hostname = self.receiveMessage(conn)
        print(f"The hostname of the client is {hostname}")
        return

    

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    server = Server()
    server.start()
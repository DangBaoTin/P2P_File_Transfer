import socket
import threading

HEADER = 64 # number of bytes of the message length
PORT = 5050
# SEVER = "192.168.100.5" # hardcode IP address of the server
SEVER = socket.gethostbyname(socket.gethostname())	# Get the IP address of the server
ADDR = (SEVER, PORT) # tuple of IP address and port number
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
server.bind(ADDR) # bind the socket to the address

# DEFINE SOME GLOBAL VARIABLES
managedFiles = dict() # list of files that the server knows
numOfClients = 0 # number of clients that the server knows

def receiveFile(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
    if msg_length: # if there is a message
        msg_length = int(msg_length) # convert the message length to integer
        filename = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 
    # print(f"{filename} need received from the client")
    ## RECEIVE THE FILE ##
    with open(filename, "wb") as f:
        bytes_read = conn.recv(BUFFER_SIZE)
        if not bytes_read:    
                # nothing is received # file transmitting is done
            print("No bytes to read")
        f.write(bytes_read)

def sendFile(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
    if msg_length: # if there is a message
        msg_length = int(msg_length) # convert the message length to integer
        filename = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 
    # print(f"{filename} need to sent to the client")
    ## SEND THE FILE ##
    with open(filename, "rb") as f: 
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
            # file transmitting is done
                break
            conn.sendall(bytes_read)
    print("File sent !")

def listFileWhenClientJoin(conn, addr):
    global managedFiles
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
    if msg_length: # if there is a message
        msg_length = int(msg_length) # convert the message length to integer
        allFiles = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client
    allFiles = allFiles.split(",") # split the string into a list
    
    for i in range(len(allFiles) - 1):

        if allFiles[i] not in managedFiles:
            managedFiles[allFiles[i]] = [addr[0]] # only store the ip - skip the port number (may need to modify later for local debug purpose) 
        else:
            managedFiles[allFiles[i]].append(addr[0]) # append the new ip and port number to the list
    print(f"Get the list of files from {addr} successfully !")
    print(managedFiles)

def updateFileListWhenClientDisconnect(conn, addr):
    global managedFiles
    managedFiles_copy = managedFiles.copy()
    for key in managedFiles:
        if addr[0] in managedFiles[key]:
            managedFiles_copy[key].remove(addr[0])
            if len(managedFiles_copy[key]) == 0:
                del managedFiles_copy[key]
    managedFiles = managedFiles_copy.copy()
    print(f"Update the list of files when {addr} disconnect successfully !")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} is connected.") # confirm the connection
    global numOfClients
    connect = True

    while connect:

        msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
        if msg_length: # if there is a message
            msg_length = int(msg_length) # convert the message length to integer
            command = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 

        if command == "publish":
            receiveFile(conn)
        elif command == "fetch":
            sendFile(conn)
        elif command == "inform":
            # print("Inform the client about the current files")
            listFileWhenClientJoin(conn, addr)
        elif command == "close":
            updateFileListWhenClientDisconnect(conn, addr)
            print(f"{addr} is disconnected")
            print(managedFiles)
            conn.close()
            connect = False
            numOfClients -= 1
    
    if numOfClients == 0:
        print("No clients connected !")
        print("Server is shutting down...")
        # server.close()
        # exit()
    
def start():
    server.listen() # start listening for connections / also block lines of code below
    print(f"[LISTENING] Server is listening on {SEVER} \n")
    while True:
        conn, addr = server.accept() # store the connection object (to send the information back) and the client address
        global numOfClients
        numOfClients += 1 # increase the number of clients
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # create a thread for each client
        thread.start() # start the thread
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
print("[STARTING] Server is starting...")
start()
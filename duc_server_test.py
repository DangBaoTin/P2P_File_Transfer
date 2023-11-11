import socket
import threading

HEADER = 64 # number of bytes of the message length
PORT = 5050
# SEVER = "192.168.100.5" # hardcode IP address of the server
SEVER = socket.gethostbyname(socket.gethostname())	# Get the IP address of the server
ADDR = (SEVER, PORT) # tuple of IP address and port number
FORMAT = 'utf-8'
BUFFER_SIZE = 4096 # send 4096 bytes each time step

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket (AF_INET: IPv4, SOCK_STREAM: TCP)
server.bind(ADDR) # bind the socket to the address

# DEFINE SOME GLOBAL VARIABLES
listManagedFiles = dict() # list of files that the server manages
numOfClients = 0 # number of clients that the server knows

def acknowledgeFiles(conn, address):
    global listManagedFiles;
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the original file name
    filename = ""
    newFilename = ""
    if msg_length:
        msg_length = int(msg_length)
        filename = conn.recv(msg_length).decode(FORMAT)

    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the new file name
    if msg_length:
        msg_length = int(msg_length)
        newFilename = conn.recv(msg_length).decode(FORMAT)
    # print(f"The {filename} with the new name {newFilename} need received from the client")

    # ADD THE FILE TO THE LIST OF MANAGED FILES
    if newFilename not in listManagedFiles:
        listManagedFiles[newFilename] = [(address, filename)]
    else:
        if (address, filename) not in listManagedFiles[newFilename]:
            listManagedFiles[newFilename].append((address, filename))
        else:
            print(f"The file {filename} is already in the server !")

    print(listManagedFiles)

def updateFileListWhenClientDisconnect(conn, address):
    global listManagedFiles
    listManagedFiles_copy = listManagedFiles.copy()
    
    for key in listManagedFiles_copy:
        for i in range(len(listManagedFiles_copy[key])):
            if listManagedFiles_copy[key][i][0] == address:
                listManagedFiles[key].pop(i)
                break
        if len(listManagedFiles[key]) == 0:
            del listManagedFiles[key]
            break

def handleFetchFile(conn, addr):
    pass

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} is connected.") # confirm the connection
    global numOfClients
    connect = True

    while connect:
        # receive the command
        msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
        if msg_length: # if there is a message
            msg_length = int(msg_length) # convert the message length to integer
            command = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 

        address = addr[1] # may be need to change to addr[0] for the real IP address

        # hadle the command
        if command == "publish":
            acknowledgeFiles(conn, address)
        elif command == "fetch":
            handleFetchFile(conn, address)
        elif command == "close":
            updateFileListWhenClientDisconnect(conn, address)
            print(f"{addr} is disconnected")
            # print(listManagedFiles)
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
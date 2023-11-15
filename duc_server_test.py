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
client_pool = dict() # list of information of client
numOfClients = 0 # number of clients that the server knows

# send the message to a client
def sendMessage(conn, msg):
    message = msg.encode(FORMAT) # encode the message
    msg_length = len(message) # get the message length
    send_length = str(msg_length).encode(FORMAT) # encode the message length
    padded_send_length = send_length + b' ' * (HEADER - len(send_length)) # pad the message length
    conn.send(padded_send_length) # send the message length
    conn.send(message) # send the message

def receiveMessage(conn):
    message = ""
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
    if msg_length: # if there is a message
        msg_length = int(msg_length) # convert the message length to integer
        message = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 
    return message
        
# receive the file infromed by the client
def acknowledgeFiles(conn, hostname):
    global listManagedFiles;

    oldFilename = receiveMessage(conn)
    newFilename = receiveMessage(conn)  

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

# update the list of managed files when a client disconnect
def updateFileListWhenClientDisconnect(conn, hostname):
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

# handle the fetch command
def handleFetchFile(conn):
    filename = receiveMessage(conn)

    # HANDLE THE FILE NOT FOUND CASE
    if filename not in listManagedFiles:
        # print("File not found !")
        sendMessage(conn, "File not found !")
        return
    else:
        sendMessage(conn, "Here are the list users have that file !")
    
    # print(listManagedFiles[filename])
    listUser = "-".join(str(element) for element in listManagedFiles[filename])
    # SEND THE LIST OF USERS HAVE THAT FILE
    # print(listUser)
    sendMessage(conn, listUser)
    ## RECEIVE THE HOSTNAME FROM CLIENT
    hostname = receiveMessage(conn)
    sendMessage(conn, client_pool[hostname]['ip'])
    sendMessage(conn, client_pool[hostname]['port_p2p'])

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} is connected.") # confirm the connection
    global numOfClients
    global client_pool
    connect = True
    # HANDLING HOSTNAME #
    while True:
        hostname = receiveMessage(conn)
        if hostname not in client_pool:
            sendMessage(conn, "Hostname registered successfully !")
            break
        else: # HANDLING THE CASE THE HOSTNAME ALREADY EXIST
            sendMessage(conn, "The hostname already exist !")
    port_p2p = receiveMessage(conn)

    # UPDATE INFORMATION IN THE CLIENT POOL
    client_pool[hostname] = {
        "ip": addr[0],
        "port_connected": addr[1],
        "port_p2p": port_p2p,
        "fname": []
    }
    # print(client_pool)


    while connect:
        # receive the command
        command = receiveMessage(conn)
        # print(f"{addr} sent {command}")
        # address = addr # may be need to change to addr[0] for the real IP address
        
        # hadle the command
        if command == "publish":
            acknowledgeFiles(conn, hostname)
        elif command == "fetch":
            handleFetchFile(conn)
        elif command == "disconnect":
            updateFileListWhenClientDisconnect(conn, hostname)
            print(f"{hostname} is disconnected")
            print(listManagedFiles)
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
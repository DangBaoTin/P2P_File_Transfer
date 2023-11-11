import socket
import os
import threading
import ast

HEADER = 64 # number of bytes of the message length
PORT = 5050
PORT_P2P = 6000
FORMAT = 'utf-8'
SERVER = "192.168.1.6"
SERVER_P2P = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT) 
BUFFER_SIZE = 4096 # send 4096 bytes each time step

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket setup
client.connect(ADDR) # connect to the server

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_P2P, PORT_P2P))

def sendMessage(conn, msg):
    message = msg.encode(FORMAT) # encode the message
    msg_length = len(message) # get the message length
    send_length = str(msg_length).encode(FORMAT) # encode the message length
    padded_send_length = send_length + b' ' * (HEADER - len(send_length)) # pad the message length
    conn.send(padded_send_length) # send the message length
    conn.send(message) # send the message

def publishFile(type, filename, newFilename):

    ## HANDLE THE FILE NOT FOUND CASE ##
    listFile = os.listdir()
    if filename not in listFile:
        print("File not found !")
        return

    ## SEND THE FILE NAME ##
    sendMessage(client, type)
    sendMessage(client, filename)
    sendMessage(client, newFilename)   

def fetchFile(type, filename):
    ## SEND THE FILE NAME ##
    sendMessage(client, type)  
    sendMessage(client, filename)

    ## RECEIVE THE LIST OF USERS HAVE THAT FILE ##
    msg_length = client.recv(HEADER).decode(FORMAT) # receive the original file name
    listUser = ""
    if msg_length:
        msg_length = int(msg_length)
        listUser = client.recv(msg_length).decode(FORMAT)
    ## CHOOSE THE LIST OF USERS ##
    print("Choose the user to download the file: ")
    listUser = listUser.split("-")
    for i in range(len(listUser)):
        print(f"{i+1}. {listUser[i]}")
    choice = int(input("Enter your choice: "))
    temp = ast.literal_eval(listUser[choice-1])
    address = temp[0]

    ## ESTABLISH THE P2P CONNECTION ##
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((address[0], 6000))  # cần thay đổi port

    ## SEND THE FILE NAME ##
    
    filename = temp[1]
    sendMessage(new_socket, filename)

    ## RECEIVE THE FILE ##
    bytes_read = client.recv(BUFFER_SIZE)
    if not bytes_read:  # nothing is received  
        print("No bytes to read")
    else: # receive the file successfully, write into the file
        with open(filename, "wb") as f:
            f.write(bytes_read)
        print("Receive the file successfully !")
    
# handling all the command
def commandHandling(string):
    string = string.split(" ")
    if string[0] == "publish": # publish the file to the server
        publishFile(string[0], string[1], string[2])
    elif string[0] == "fetch": # fetch the file from the server
        fetchFile(string[0], string[1])
    elif string[0] == "close":
        sendMessage(client, string[0])
        client.close()
    return

def handle_peer(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    filename = ""
    msg_length = conn.recv(HEADER).decode(FORMAT) # receive the file name
    if msg_length: # if there is a message
        msg_length = int(msg_length) # convert the message length to integer
        filename = conn.recv(msg_length).decode(FORMAT) # receive the actual message from the client 
    
    with open(filename, "rb") as f: 
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
            # file transmitting is done
                break
            conn.sendall(bytes_read)
    print("File sent !")

    conn.close()

def start():
    server_socket.listen() # start listening for connections / also block lines of code below
    print(f"[LISTENING] Server is listening on {SERVER} \n")
    while True:
        conn, addr = server_socket.accept() 
        thread = threading.Thread(target=handle_peer, args=(conn, addr)) # create a thread for each client
        thread.start() # start the thread
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def main():
    thread1 = threading.Thread(target=start)
    thread2 = threading.Thread(target=main2)
    thread1.start()
    thread2.start()

def main2():
    # while True:
    #     command = input("Enter your command: ")
    #     commandHandling(command)
    #     if command == "close":
    #         break
    commandHandling("publish receive.txt receive")
    input("Press Enter to continue...")
    commandHandling("close")

def main3(): # test the fetch function
    commandHandling("fetch receive")
    input("Press Enter to continue...")
    commandHandling("close")

main()


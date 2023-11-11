import socket
import os

HEADER = 64 # number of bytes of the message length
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.6"
ADDR = (SERVER, PORT) 
BUFFER_SIZE = 4096 # send 4096 bytes each time step

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket setup
client.connect(ADDR) # connect to the server

def sendMessage(msg):
    message = msg.encode(FORMAT) # encode the message
    msg_length = len(message) # get the message length
    send_length = str(msg_length).encode(FORMAT) # encode the message length
    padded_send_length = send_length + b' ' * (HEADER - len(send_length)) # pad the message length
    client.send(padded_send_length) # send the message length
    client.send(message) # send the message

def publishFile(type, filename, newFilename):
    ## SEND THE FILE NAME ##
    sendMessage(type)
    sendMessage(newFilename)
    ## SEND THE FILE ##
    with open(filename, "rb") as f: 
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
            # file transmitting is done
                break
            client.sendall(bytes_read)
        print(client.recv(HEADER).decode(FORMAT)) # receive the confirmation message from the server

def fetchFile(type, filename):
    ## SEND THE FILE NAME ##
    sendMessage(type)  
    sendMessage(filename)
    ## RECEIVE THE FILE ##
    bytes_read = client.recv(BUFFER_SIZE)
    if not bytes_read:  # nothing is received  
        print("No bytes to read")
    else: # receive the file successfully, write into the file
        with open(filename, "wb") as f:
            f.write(bytes_read)
        print("Receive the file successfully !")

def inform():
    listFile = os.listdir()
    allFiles = ",".join(str(element) for element in listFile)
    sendMessage(allFiles)
    
# handling all the command
def commandHandling(string):
    string = string.split(" ")
    if string[0] == "publish": # publish the file to the server
        publishFile(string[0], string[1], string[2])
    elif string[0] == "fetch": # fetch the file from the server
        fetchFile(string[0], string[1])
    elif string[0] == "inform": # inform the server about all the current files
        sendMessage(string[0])
        inform()
    elif string[0] == "close":
        sendMessage(string[0])
        client.close()
    return

# commandHandling("publish send.txt receive.txt")
# commandHandling("fetch receive.txt")
commandHandling("inform")
input("Press Enter to continue...")
commandHandling("close")


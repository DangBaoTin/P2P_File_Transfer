import socket
import os
import threading
import ast

HEADER = 64 # number of bytes of the message length
PORT = 5050
PORT_P2P = 0 # random port
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
SERVER_P2P = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT) 
ADDR_P2P = (SERVER_P2P, PORT_P2P)
BUFFER_SIZE = 4096 # send 4096 bytes each time step

def sendMessage(conn, msg):
    message = msg.encode(FORMAT) # encode the message
    msg_length = len(message) # get the message length
    send_length = str(msg_length).encode(FORMAT) # encode the message length
    padded_send_length = send_length + b' ' * (HEADER - len(send_length)) # pad the message length
    conn.send(padded_send_length) # send the message length
    conn.send(message) # send the message

def receiveMessage(conn):
    message = ""
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length) 
        message = conn.recv(msg_length).decode(FORMAT)
    return message

def handlePeer(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    filename = receiveMessage(conn)
    print(filename)
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

class Client:
    def __init__(self):
        # create a socket to connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client.connect(ADDR)

        # create a socket to listen other clients
        self.p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_server_socket.bind(ADDR_P2P)

    def publishFile(self, type, filename, newFilename):
        ## HANDLE THE FILE NOT FOUND CASE ##
        listFile = os.listdir()
        if filename not in listFile:
            print("File not found !")
            return

        ## SEND THE TYPE OF COMMAND AND THE FILE NAME ##
        sendMessage(self.client, type)
        sendMessage(self.client, filename)
        sendMessage(self.client, newFilename)   

    def fetchFile(self, type, filename):
        ## SEND THE FILE NAME ##
        sendMessage(self.client, type)  
        sendMessage(self.client, filename)

        ## FILE NOT FOUND CASE
        response = receiveMessage(self.client)
        print(response)
        if response.startswith("File not found !"):
            return

        ## RECEIVE THE LIST OF USERS HAVE THAT FILE ##
        listUser = receiveMessage(self.client)
        
        ## CHOOSE THE LIST OF USERS ##
        print("Choose one user to download the file: ")
        listUser = listUser.split("-")
        for i in range(len(listUser)):
            print(f"{i+1}. {listUser[i]}")
        choice = int(input("Enter your choice: "))
        while choice>len(listUser):
            print("Please choose a number in range !")
            choice = int(input("Re-enter your choice: "))

        hostname = ast.literal_eval(listUser[choice-1])[0]
        filename = ast.literal_eval(listUser[choice-1])[1]
        ## SEND THE HOSTNAME BACK TO SERVER ##  
        sendMessage(self.client, hostname)

        ip = receiveMessage(self.client)
        port_p2p = receiveMessage(self.client)
        print(f"port p2p int {int(port_p2p)} and original {port_p2p}")

        ## ESTABLISH THE P2P CONNECTION ##
        p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p2p_socket.connect((ip, int(port_p2p)))  # cần thay đổi port
        
        ## SEND THE FILE NAME TO THE PEER ##
        sendMessage(p2p_socket, filename)

        ## RECEIVE THE FILE ##
        bytes_read = p2p_socket.recv(BUFFER_SIZE)
        if not bytes_read:  # nothing is received  
            print("No bytes to read")
        else: # receive the file successfully, write into the file
            with open(filename, "wb") as f:
                f.write(bytes_read)
            print("Receive the file successfully !")

    def commandHandler(self, command):
        command = command.split()
        if command[0] == "publish":
            self.publishFile(command[0], command[1], command[2])
        elif command[0] == "fetch":
            self.fetchFile(command[0], command[1])
        elif command[0] == "disconnect":
            sendMessage(self.client, command[0])
            self.client.close()
            exit()
        else:
            print("Invalid command !")

    def handleP2PConnection(self):
        self.p2p_server_socket.listen()
        # print(f"[LISTENING] P2P is listening on port {self.p2p_server_socket.getsockname()[1]} \n")
        while True:
            conn, addr = self.p2p_server_socket.accept()
            print("Connect p2p successfully !")
            thread = threading.Thread(target=handlePeer, args=(conn, addr))
            thread.start()

    def start(self):
        # start the thread to listen other clients
        thread_response_handler = threading.Thread(target=self.handleP2PConnection)
        thread_response_handler.start()

        # REGISTER THE HOST NAME #
        hostname = input("Enter your hostname:")
        sendMessage(self.client, hostname)
        response = receiveMessage(self.client)
        print(response)
        while response.startswith("The hostname already exist !"):
            hostname = input("Enter another name: ")
            sendMessage(self.client, hostname)
            response = receiveMessage(self.client)
            
        # SEND THE PORT HOST P2P
        port_p2p = self.p2p_server_socket.getsockname()[1]
        sendMessage(self.client, str(port_p2p))

        while True:
            try:
                command = input("Enter command: ")
                self.commandHandler(command)

            except KeyboardInterrupt:
                print("Client closed.")
                break

if __name__ == "__main__":
    client = Client()
    client.start()

import time
import socket
import threading

PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
HEADER = 1024
FORMAT = "utf-8"

def main(addr, hostname):
    print("Starting client.")
    # Socket type TCP: SOCK_STREAM : TCP, SOCK_DGRAM : UDP
    client= socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(addr)

    # Sending the hostname to the server. 
    client.send(hostname.encode(FORMAT))
    msg = client.recv(HEADER).decode(FORMAT)

    client.send("publish file1.txt file1.txt".encode(FORMAT))
    time.sleep(1)

    client.send("publish file2.txt file2.txt".encode(FORMAT))
    time.sleep(1)

    client.send("publish file3.txt file2.txt".encode(FORMAT))
    time.sleep(5)
    
    client.close()

if __name__ == "__main__":
    hostname = input('Enter hostname:')
    main(ADDR, hostname)

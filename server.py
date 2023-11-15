import socket
import threading
from interface import serverInterface

# Sever configuration  
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
HEADER = 1024 # Buffer size
ADDR = (HOST, PORT)
FORMAT = "utf-8"

class Server:
    def __init__(self, ADDR):
        print(f"[STARTING] Server starting at ADDRESS: {ADDR[0]}, PORT: {ADDR[1]}")
        # Socket type TCP: SOCK_STREAM : TCP, SOCK_DGRAM : UDP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.bind(ADDR)
        
        # Client pool format:
        # {
        #   'hostname': {
        #       "connection":
        #       "address":
        #       "files":
        #   }
        # }
        self.client_pool = dict()

    def listen(self):
        print("[LISTENING] Server is listening.")
        self.server.listen()
    
    def close(self):
        print("Server close connection.")
        self.server.close()
    
    def accept(self):
        # Accepting connection from client 
        conn, addr = self.server.accept()

        # Must have client hostname
        hostname = conn.recv(HEADER)
        if not hostname:
            return None
        hostname = str(hostname.decode(FORMAT))
        conn.send("Received".encode(FORMAT))

        # Add client to client pool
        self.client_pool[hostname] = {
            "connection": conn,
            "address": addr,
            "files": []
        }
        
        #print(f"[ACCEPTING] Accepting connection from ADDRESS: {addr[0]}, PORT: {addr[1]}")
        return hostname
    
    def ping(self, hostname):
        ping_status = False
        if self.client_pool.get(hostname):
            try:
                self.client_pool[hostname]["connection"].send("Connection".encode(FORMAT))
                ping_status = True
            except:
                ping_status = False

            if not ping_status:
                self.client_pool.pop(hostname)
        return ping_status
    
    def discover(self, hostname):
        if self.ping(hostname):
            return self.client_pool[hostname]["files"]
        else:
            return None

    def publish(self, hostname, lname, fname):
        file = (lname, fname)
        if file not in self.client_pool[hostname]['files']: 
            self.client_pool[hostname]['files'].append((lname, fname))

    def fetch(self, hostname, fname):
        pass

def clientHandler(server, hostname):
    conn = server.client_pool[hostname]["connection"]
    while True:
        try: # client ngat ket noi
            data = conn.recv(HEADER)
            if not data:
                break
            data = str(data.decode(FORMAT))
        except:
            # Client disconnected
            return
        
        try:
            cmd = data.split(" ")
        except:
            continue

        if cmd[0] == "publish":
            server.publish(hostname, cmd[1], cmd[2])
        elif cmd[0] == "fetch":
            server.fetch(hostname, cmd[1])

def serverHandler(server):
    while True:
        # Accept connection from client
        try:
            hostname = server.accept()
        except:
            return
        
        if hostname is None:
            continue

        client_thread = threading.Thread(target=clientHandler, args=(server, hostname))
        client_thread.start()
    
def main(ADDR):
    server = Server(ADDR)
    server.listen()

    # Starting server thread
    server_thread = threading.Thread(target=serverHandler, args=(server,))
    server_thread.start()

    # Starting server interface
    serverInterface(server)

    server.close()
    server_thread.join()
    
if __name__ == "__main__":
    main(ADDR)
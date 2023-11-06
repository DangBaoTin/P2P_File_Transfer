# Adapted from https://github.com/Vishal-shakaya/python_socket/blob/master/server.py

import socket 

global_connection = []
def Handler(connection):
    # Do something #
    connected = True 
    while connected:
        data = connection.recv(HEADER)
        if not data:
            # print_lock.release()
            print('bye')
            break;  
        print(str(data.decode(FORMAT)))
        connection.send('message_send'.encode(FORMAT))
    connection.close()
        
def Start():
    # 1. Listen incomming connection: 
    server.listen() 
    # 2. Accept all connection :
    while True:
        # 3. Create Client Thread :
        conn, addr = server.accept()
        global_connection.append(conn)

        print(f'[CONNECTED]-> {addr}') # print_lock.acquire()
        
        start_new_thread(ClientHandler, (conn,))

    # 4. Close the connection :   
    server.close()
    
print('****[ SERVER STARTING ]****')
Start()

# -> Interface
# -> Listening
class Client:
    def __init__(self):
        pass

    def publish(self):
        '''
        Send message to signal that the client has this file
        '''
        pass

    def fetch(self):
        '''
        Send message to server to find the client that contains the file 
        '''
        pass
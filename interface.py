from tabulate import tabulate

def clientInterface(client):
    # Something
    pass

def serverInterface(server):
    while True:
        # User command must be format: command value
        user_cmd = input("server>").strip() 
        try:
            # Handling cases when user input single command
            cmd, value = user_cmd.split(" ")
        except:
            cmd = user_cmd

        if cmd == "ping":
            ping_status = server.ping(hostname=value)
            if ping_status:
                print(f"Hostname \'{value}\' is connecting.")
            else:
                print(f"Hostname \'{value}\' has disconected.")
        elif cmd == "discover":
            files = server.discover(hostname=value)
            if files is None:
                print(f"Hostname \'{value}\' has disconected.")
            else:
                print(f"Hostname \'{value}\'")
                table = [['LName', 'FName']]
                table.extend(files)
                print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

        elif cmd == "exit":
            break
        else:
            print(f"\'{cmd}\' is not recognized as a supported command.")
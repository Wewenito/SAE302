import socket
import threading
from command_handler import CHandler

class Server_handle:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.current_threads = []
    
    def connect_server(self):
        try:
            self.server_socket = socket.socket()
            self.server_socket.bind((self.host,self.port))
        except:
            self.server_socket = None

    def check_connection(self) -> str:
        if self.server_socket:
            return "OK"
        else:
            return "ERROR"

    def connect_new_client(self):
        self.server_socket.listen(50)
        self.conn, self.address = self.server_socket.accept()

        user_name = self.conn.recv(1024).decode()
        connection = [user_name,self.conn]
            

        #print("New client connection established.")
        #print(f"User name -> {connection[0]}")
        #print(f"Conn and Adress objects -> {connection[1]}")
        print(f"Current number of active connections : {len(self.current_threads)}")
        for client in self.current_threads:
            print(f"Client : '{client[0]}'")
            #print(f"Values for conn : '{client[1]}'")

        return connection

    def disconnect_and_clear_client(self, client_name):
        for client in self.current_threads:
            if client_name == client[0]:
                print(f"deleting user {client[0]} from cache")
                self.current_threads.remove(client)
        
        print("Items left in self.current_threads :")
        print(self.current_threads)

    def send_broadcast_message(self, message):
        print(len(self.current_threads))
        for client in self.current_threads:
            print(f"sending message for {client[0]}")
            client[1].send(message.encode())

    #this function will be used when a client sends a message for a particular task
    def listen_for_order(self, client_conn):
        flag = False
        error = None
        while flag == False:
            order = client_conn[1].recv(1024).decode()
            if not order:
                # raise socket.error("Connection closed by client")
                flag = True
                print("There is a disconnection / loop")
                print("disconnecting client")
                self.disconnect_and_clear_client(client_conn[0])
                break

            print(f"Message received from {client_conn[0]}")

            try:
                action = CHandler(order)
                print(f"CHandler done. Action to execute : {action[0]}")
            except Exception as E:
                print("-----------------------------------------------------------------------------------")
                print("Error during listen for order :")
                print(E)
                print("-----------------------------------------------------------------------------------")

            match action[0]:
                case "BROADCAST":
                    try:
                        self.send_broadcast_message(action[1])
                    except Exception as E:
                        print(E)
                case "BYE":
                    print(f"Disconnecting client")
                    confirmation_message = "OK BYE"
                    client_conn[1].send(confirmation_message.encode())
                case "UNKNOWN":
                    pass
                case "SINGLE KEYWORD":
                    pass
                case _:
                    pass


            # rep = "Query executed well"
            # client_conn[1].send(rep.encode())
        else:
            print("--------------------------")
            print(f"A problem has been encountered with the client {client_conn[0]} and it is no longer available.")
            print(f"Disconnecting the client '{client_conn[0]}'")
            self.disconnect_and_clear_client(client_conn[0])
            print("thread deleted")
            print("-------------------------")

    def setup_connection_listener(self):
        while True:
            print("Starting to listen for new clients")
            result = self.connect_new_client()

            order_thread_for_this_client = threading.Thread (target=self.listen_for_order, name=result[0], args=(result,))
            order_thread_for_this_client.start()
            print(f"Here is the return for starting thread for this client : {result}")



        






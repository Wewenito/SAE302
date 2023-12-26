import socket, threading
from sys_x import display_error, generate_uid
from sql_Handler import *

class Server_handle:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.current_threads = []
        self.listening = True
    
    def connect_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server_socket.bind((self.host,self.port))

    
    def listen_for_conns(self):
        while self.listening == True:
            self.server_socket.listen(200)
            self.conn, self.address = self.server_socket.accept()

            action = self.conn.recv(1024).decode()
            #for the array below : 
            #this is available for every connection to the server.
            #first one is the name, second is the connection object, third one is wether if the user is logged or not.
            connection = [generate_uid(), self.conn, False]

            self.current_threads.append(connection)

            print(f"Current number of active connections : {len(self.current_threads)}")
            for client in self.current_threads:
                print(f"Client : '{client[0]}'")

            if action == "/login":
                #while connection[2] == False:
                log_user = threading.Thread (target=self.log_user, name=connection[0], args=(connection,))
                log_user.start()
                    
                #log_user.join()
            elif action == "/register":
                self.register_user()


    def show_current_clients(self):
        print(f"Total number of clients = {len(self.current_threads)}")
        for clients in self.current_threads:
            print(f"Client - {clients[0]} -> IS LOGGED ? {clients[2]}")

    def log_user(self, client_conn):#the parameter is the connection established with the client.
        try:
            print("[Server_handle log_user starts]")
            client_conn[1].send("INIT_LOGIN_PROCESS".encode())


            while client_conn[2] == False:
                print("waiting for the correct user data, ")
                response = client_conn[1].recv(1024).decode()
                
                print(f"response from {client_conn[0]} : {response}")

                
                
                #Here we check if user exists,
                mydb = establish_connection()

                user_data_proposed = response.split("|")
                if does_user_exists(mydb, user_data_proposed[0]):
                    #Then we actually check if his credentials are OK
                    user_data_from_db = get_user_info(mydb, user_data_proposed[0])

                    print(f"gathered data from db : {user_data_from_db}")
                    if user_data_proposed[1] == user_data_from_db['Password']:
                        client_conn[1].send("LOGIN_PROCESS_STEP_2|OK".encode())
                        ack_complete_log = client_conn[1].recv(1024).decode()
                        if ack_complete_log == "LOGIN_ACK_DONE":
                            print(f"Connection '{client_conn[0]}' is now logged in.")
                            
                            #Adding to connection a "connection[2]" containing wether the client is logged or not.
                            client_conn[2] = True
                            print("[Server_handle log_user ends]")

                            #once user is fully logged, we setup a listener in the main loop to interact with him
                            main_loop_user = threading.Thread (target=self.listen_to_user, name=client_conn[0], args=(client_conn,))
                            main_loop_user.start()
                            return
                    else:
                        print(f"User sent password is not right -> expected : {user_data_from_db['Password']}, received : {user_data_proposed[1]}")
                        client_conn[1].send("LOGIN_PROCESS_STEP_2|NOK|WRONG_PASSWORD".encode())
                else:
                    print(f"User sent does not exist -> {user_data_proposed[0]}")
                    client_conn[1].send("LOGIN_PROCESS_STEP_2|NOK|USER_DOES_NOT_EXIST".encode())
        except BrokenPipeError as E:
            display_error("The client has disconnected. Taking him of the current_threads list.\n\n", E)
            self.disconnect_and_clear_client(client_conn[0])
    
    
    def register_user(self):
        print("reg user")
        pass

    
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


    def listen_to_user(self, connection):#This can be considered the MAIN LOOP for each client to send messages in.
        print("[Server_handle listen_to_user starts]")
        while True:
            message = connection[1].recv(1024).decode()

            if message == "":
                print("brocken pipe")
                self.disconnect_and_clear_client(connection[0])
                print("[Server_handle listen_to_user ends]")
                break
            else:
                message_processed = self.CHandler(message)
                print(f"\nMessage from '{connection[0]}' which log status is {connection[2]} : {message}")
                print(f"Message processed is : {message_processed}")

                if message_processed[0] == "BROADCAST":
                    self.send_broadcast_message(message_processed[1])

        print("[Server_handle listen_to_user ends]")


    def CHandler(self, command):
        case = None

        first_space_index = command.find(' ')

        if command.startswith('/'):
            case = 1
        else:
            case = 2


        if case == 1: #If a command is sent
            if first_space_index != -1: #If command is a command keyword + string (ex : /join Salon1 or /broadcast this is a global broadcast)
                split = [command[:first_space_index], command[first_space_index + 1:]]

                match split[0]:
                        case "/broadcast":
                            return ["BROADCAST", split[1]]
                        case _:
                            return ["SINGLE KEYWORD", split[1]]
            else: #if command is just a single keyword (ex : /bye  or /logout)
                split = [command]
                match split[0]:
                    case "/bye":
                        return ["BYE", None]
                    case _:
                        return ["UNKNOWN", None]
        elif case == 2: #If only a random string is sent
            return ["UNKNOWN_CASE_2", None]
        else:
            return ["UNKNOWN", None]
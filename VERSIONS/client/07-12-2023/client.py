import socket, threading, select, os, time


class Client_handle:
    def __init__(self) -> None:
        self.client_name = None
        self.client_socket = None
        self.running = None
        self.logged_in = False #this variable sets to True once client is logged in to the server. use this to prevent actions in case user is not logged.


    def connect_to_server(self, server_IP, server_PORT):
        self.client_socket = socket.socket()
        self.client_socket.connect((server_IP, server_PORT))

    def send_message_server(self, message):
        self.client_socket.send(message.encode())

    def terminate_client(self):
        # Add any cleanup or termination logic here
        self.client_socket.close()
        os._exit(0)  # Forcefully exit the client process

    def send_user_messages(self):
        while True:
            try:
                # Get user input and send it to the server
                user_input = input("\n   > ")
                self.send_message_server(user_input)
            except Exception as e:
                print(f"Error sending message: {e}")
                break

    def login_process(self):
        print("[Client_handle login_process starts]")
        while self.logged_in == False:
                credentials_username = str(input("Please enter your username : \n   > "))
                credentials_password = str(input("Please enter your password : \n   > "))
                
                user_data = credentials_username + "|" + credentials_password

                self.client_socket.send(user_data.encode())

                server_response = self.client_socket.recv(1024).decode()
                if server_response == "LOGIN_PROCESS_STEP_2|OK":
                    print("NOW WE ARE WELL LOGGED IN")
                    self.client_socket.send("LOGIN_ACK_DONE".encode())
                    self.logged_in = True
                    print("You can now speak to the server by sending a message.")
                    print("[Client_handle login_process ends]")
                    break  # Exit the loop after successful login
                elif server_response == "LOGIN_PROCESS_STEP_2|NOK|USER_DOES_NOT_EXIST":
                    print("This user does not exist. Please type in the infos again.")
                    pass
                    # here send the user back to login asking for creds
                elif server_response == "LOGIN_PROCESS_STEP_2|NOK|WRONG_PASSWORD":
                    print("The password given is not right. Please try again.")
                    pass 
                    # Optionally, you can add a loop or retry logic here
                


    def listen_server_messages(self):
        """ READ-ME
            This function is basically the main loop of the client.
            While the client is not logged in, we initiate and make sure that he logs in or registers.
            Once the user is well logged in (self.logged_in = True), then we start two threads :
                    - One listens in case the server sends messages
                    - One takes-in an input to send to the server.
        """
        print("[Client_handle listen_server_messages starts]")
        while self.logged_in == False:
            try:
                # Use select to wait for either user input or incoming server messages
                inputs, _, _ = select.select([self.client_socket], [], [], 1)
                

                for ready_socket in inputs:
                    if ready_socket == self.client_socket:
                        # Handle incoming server message
                        message = self.client_socket.recv(1024).decode()
                        if message == "INIT_LOGIN_PROCESS":
                            self.login_process()
                            pass
                        else:
                            print(f"Message from server: {message}", end='\n   > ', flush=True)
                        if not message:
                            print("server disconnected")
                            return
            except Exception as e:
                print(f"Error: {e}")
                break
        else:
            def listen_server():
                print("[Client_handle listen_server starts]")
                while self.logged_in == True:
                    try:
                        message = self.client_socket.recv(1024).decode()
                        if message == "message":
                            print("zebi")
                        else:
                            print(f"Message from server: {message}", end='\n   > ', flush=True)
                        if not message:
                            print("server disconnected")
                            print("[Client_handle listen_server ends]")
                            return
                    except Exception as e:
                        print(f"Error: {e}")
                        self.logged_in = False
                        print("[Client_handle listen_server ends]")
                        break

        
            user_input_thread = threading.Thread(target=self.send_user_messages)
            server_thread = threading.Thread(target=listen_server)

            user_input_thread.start()
            server_thread.start()

            user_input_thread.join()
            server_thread.join()

            print("[Client_handle listen_server_messages ends]")
            


        #CHATGPT
        # def listen_server():
        #     while self.logged_in == True:
        #         try:
        #             message = self.client_socket.recv(1024).decode()
        #             if message == "INIT_LOGIN_PROCESS":
        #                 self.login_process()
        #             else:
        #                 print(f"Message from server: {message}", end='\n   > ', flush=True)
        #             if not message:
        #                 print("server disconnected")
        #                 return
        #         except Exception as e:
        #             print(f"Error: {e}")
        #             break

        # user_input_thread = threading.Thread(target=self.send_user_messages)
        # server_thread = threading.Thread(target=listen_server)

        # user_input_thread.start()
        # server_thread.start()

        # user_input_thread.join()
        # server_thread.join()


        #ORIGINAL
        # while True:
        #     try:
        #         # Use select to wait for either user input or incoming server messages
        #         inputs, _, _ = select.select([self.client_socket], [], [], 1)
                

        #         for ready_socket in inputs:
        #             if ready_socket == self.client_socket:
        #                 # Handle incoming server message
        #                 message = self.client_socket.recv(1024).decode()
        #                 if message == "INIT_LOGIN_PROCESS":
        #                     self.login_process()
        #                     pass
        #                 else:
        #                     print(f"Message from server: {message}", end='\n   > ', flush=True)
        #                 if not message:
        #                     print("server disconnected")
        #                     return
        #     except Exception as e:
        #         print(f"Error: {e}")
        #         break
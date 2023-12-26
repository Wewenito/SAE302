import socket 
import threading
import select
import os, time

class Client_handle:
    def __init__(self, client_name) -> None:
        self.client_name = client_name
        self.client_socket = None
        pass

    def connect_to_server(self, serv_ip, serv_port):
        self.client_socket = socket.socket()

        try:
            self.client_socket.connect((serv_ip, serv_port))
            print("client is connected")
        except Exception as E:
            print("Error during connection of the client.. please retry")
            print(E)

    def send_message(self, message):
        self.client_socket.send(message.encode())

    def listen_server_messages(self):
        while True:
            try:
                # Use select to wait for either user input or incoming server messages
                inputs, _, _ = select.select([self.client_socket], [], [])

                for ready_socket in inputs:
                    if ready_socket == self.client_socket:
                        # Handle incoming server message
                        message = self.client_socket.recv(1024).decode()
                        print(message)
                        if message == "OK BYE":
                            print("Client has been terminated.\n window will close in 5 secs")
                            time.sleep(5)
                            self.terminate_client()
                            return
            except Exception as e:
                print(f"Error: {e}")
                break

    def terminate_client(self):
        # Add any cleanup or termination logic here
        self.client_socket.close()
        os._exit(0)  # Forcefully exit the client process

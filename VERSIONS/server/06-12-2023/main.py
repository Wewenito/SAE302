from server import Server_handle
import threading
import time

connection_loop = False

def setup() -> object:
    print("Creating a server instance")    
    
    try:
        server = Server_handle('0.0.0.0', 11111)
        server.connect_server()
    except Exception as E:
        print(E)

    print(f"SERVER STATUS -> {server.check_connection()}")

    return server



#RETURN HERE FOR WHEN IT WORKED

if __name__ == '__main__':

    try:
        server = setup()
    except:
        print("error during server setup, please retry")

    #here we start the thread that will continuously check for new connections
    connection_listener_thread = threading.Thread (target=server.setup_connection_listener)
    connection_listener_thread.start()


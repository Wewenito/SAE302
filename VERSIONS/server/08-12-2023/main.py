from server import Server_handle
import threading


def console_input_handler(server_instance):
    while True:
        user_input = input("Enter a message for the server (or 'exit' to quit): ")
        if user_input.lower() == '/show_clients':
            server_instance.show_current_clients()
        else:
            print("unassigned")

def setup():
    try:
        server = Server_handle('0.0.0.0', 11111)
        server.connect_server()
        return server
    except Exception as E:
        print("There has been an error while setting up the server")
        print(E)
        return 400



server = setup()

if __name__ == '__main__' and server != 400:
    print("Server is up and running.")
    connection_listener_server = threading.Thread (target=server.listen_for_conns)
    connection_listener_server.start()

    console_input_thread = threading.Thread(target=console_input_handler, args=(server,))
    console_input_thread.start()



from server import Server_handle
import threading, time, signal, os


def console_input_handler(server_instance, exit_flag):
    while not exit_flag.is_set():
        user_input = input("Enter a message for the server (or 'exit' to quit): ")
        if user_input.lower() == '/show_clients':
            server_instance.show_current_clients()
        elif user_input.lower().split(" ")[0] == "/broadcast":
            server_instance.send_broadcast_message(user_input.split(" ")[1])
        elif user_input.lower().split(" ")[0] == "/kill":
            server_instance.send_broadcast_message("SERVER_IS_TURNING_OFF")
            exit_flag.set()
            pass
        elif user_input.lower().split(" ")[0] == "/ban":
            user_to_ban = user_input.split(" ")[1]
            if server_instance.ban_user(user_to_ban) == False:
                print("This user does not exist.")
        elif user_input.lower().split(" ")[0] == "/kick":
            user_to_kick = user_input.split(" ")[1]
            duration_of_the_kick = user_input.split(" ")[2]#in seconds
            if server_instance.kick_user(user_to_kick, duration_of_the_kick) == False:
                print("This user does not exist")
        elif user_input.lower().split(" ")[0] == "/threads":
            for thread in threading.enumerate():
                print(f"Thread name: {thread.name}, Thread ID: {thread.ident}")
        else:
            print("unassigned")

    print("console_input_handler stops (flag set)")

def setup():
    try:
        server = Server_handle('0.0.0.0', 11111)
        server.connect_server()
        return server
    except Exception as E:
        print("There has been an error while setting up the server")
        print(E)
        return 400



if __name__ == '__main__':
    server = setup()

    if server != 400:
        print("Server is up and running.")
        exit_flag = threading.Event()
    
        connection_listener_server = threading.Thread (target=server.listen_for_conns, args=(exit_flag,))
        connection_listener_server.start()

        console_input_thread = threading.Thread(target=console_input_handler, args=(server, exit_flag))
        console_input_thread.start()

        try:
            while not exit_flag.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")


        # console_input_thread._stop()
        # print("console_input_thread stopped")
        # connection_listener_server._stop()
        # print("connection_listener_server stopped")
        # server.destroy()
        

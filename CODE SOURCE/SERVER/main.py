from server import Server_handle
import threading, time, signal, os, socket
from sql_Handler import establish_connection, close_connection, does_user_exists, get_user_info, update_user_as_admin, set_new_user_password

def console_input_handler(server_instance, exit_flag):
    is_console_logged = False
        
    while not exit_flag.is_set():
        if is_console_logged == True:
            user_input = input("Enter a message for the server (or 'exit' to quit): ")
            if user_input.lower() == '/show_clients':
                server_instance.show_current_clients()
            elif user_input.lower().split(" ")[0] == "/broadcast":
                command, message = user_input.split(" ", 1)
                command = command[1:]
                server_instance.send_broadcast_message(message)
            elif user_input.lower().split(" ")[0] == "/change_password":
                user_to_change_password = user_input.split(" ")[1]
                mydb = establish_connection()
                if does_user_exists(mydb, user_to_change_password):
                    new_password = input("Please enter the new password for this user -> ")
                    confirm_new_password = input("Confirm the password -> ")
                    if new_password == confirm_new_password:
                        query = set_new_user_password(mydb, user_to_change_password, new_password)
                        if query[0]:
                            print("User password has been succesfully changed !")
                        else:
                            print(f"Error during change of password : {query[1]}")
                    else:
                        print("\nThe two passwords do not match, please retry")
                else:
                    print(f"The user '{user_to_change_password}' does not exist.")
                close_connection(mydb)
            elif user_input.lower().split(" ")[0] == "/make_admin":
                user_to_make_admin = user_input.split(" ")[1]
                mydb = establish_connection()
                if does_user_exists(mydb, user_to_make_admin):
                    print("Setting this user as an admin")
                    user_data = get_user_info(mydb, user_to_make_admin)

                    query = update_user_as_admin(mydb, user_to_make_admin, user_data['id'])
                    if query[0]:
                        print("User has been succesfully set as an admin !")
                    else:
                        print(f"Error encountered while setting up user as an admin : \n\n{query[1]}")
                else:
                    print(f"The user '{user_to_make_admin}' does not exist.")
                close_connection(mydb)
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
                print("Commande inconnue ou syntaxe incorrecte, merci de vérifier la commande entrée.")
        else:
            print("To send commands via the server, you need to be logged-in as an admin.\n\nPlease enter your credentials here below : \n\n")
            username = input("Enter your admin username -> ")
            password = input("Enter your password -> ")

            mydb = establish_connection()

            print("Connection established !")

            if does_user_exists(mydb, username):
                user_data = get_user_info(mydb, username)
                if user_data['User_type'] == 'ADMIN':
                    if user_data['Password'] == password:
                        print(f"\n\nLOGIN SUCCESSFUL\nNow enabling commands for this console with the user {user_data['Username']}")
                        is_console_logged = True
                        pass
                    else:
                        print("\n\nThe password entered is incorrect for this user, please retry.")
                        pass
                else:
                    print("\n\nThis user is not an admin, you cannot login with it.")
                    pass
            else:
                print("\n\nThis user does not exist, please check your spelling.")
                pass

            close_connection(mydb)

    print("console_input_handler stops (flag set)")

def setup():
    try:
        server = Server_handle("0.0.0.0", 11111)
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
        

import socket, threading
from sys_x import display_error, generate_uid
from sql_Handler import *


class Server_handle:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.current_threads = [] #contains arrays with [connection name (4digits), connect object, user logged or not (bool)]
        self.user_data = []  #contains arrays with [associated connection name, user_data_array]

    def destroy(self):
        try:
            self.server_socket.close()
            print("Server socket destroyed")
        except Exception as E:
            print("Error while trying to kill server..")
            print(E)
            
    def connect_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server_socket.bind((self.host,self.port))

    def listen_for_conns(self, exit_flag):
        self.server_socket.settimeout(2)
        while not exit_flag.is_set():
            try:
                self.server_socket.listen(20)
                self.conn, self.address = self.server_socket.accept()
                print("New conn detected, pass all this below in a temp thread in case two people hit login at same time")
                #tbd

                action = self.conn.recv(1024).decode()#this part can block the /kill function until user has clicked the login / register button
                #for the array below : 
                #this is available for every connection to the server.
                #first one is the name, second is the connection object, third one is wether if the user is logged or not.
                connection = [generate_uid(), self.conn, False]

                self.current_threads.append(connection)

                print(f"Current number of active connections : {len(self.current_threads)}")
                for client in self.current_threads:
                    print(f"Client : '{client[0]}'")

                if action == "/login":
                    log_user = threading.Thread (target=self.log_user, name=connection[0], args=(connection, exit_flag))
                    log_user.start()
                elif action == "/register":
                    reg_user = threading.Thread(target=self.register_user, name=connection[0], args=(connection, exit_flag))
                    reg_user.start()
            except socket.timeout:
                pass
            except Exception as E:
                pass
        else:
            print("listen_for_conns stops (flag set)")

    def kick_user(self, user_to_kick, duration_of_the_kick):#in seconds
        print("[Server_handle kick_user starts]")
        print(f"kick user : {user_to_kick} for {duration_of_the_kick} seconds")
        
        mydb = establish_connection()

        if does_user_exists(mydb, user_to_kick):
            print("This user exists")
        else:
            print("User does not exist")
            return False
        
        user_data = get_user_info(mydb, user_to_kick)

        kick = set_kick_for_user(mydb, user_data['id'], duration_of_the_kick)

        if kick[0] == True:
            print("User has been succesfully kicked")
        elif kick[0] == False:
            if kick[1] == "USER_IS_BANNED":
                print("You cannot assign a kick to a user that has been banned.")
                return False
            else:
                print(f"Error during the kick process.\nError raised : \n\n{kick[1]}")

        #Now we check if user is currently connected, if so, we disconnect him
        connection = None
        for user in self.user_data:
            if user[1]['Username'] == user_to_kick:
                connection = user[0]
                break

        if connection is not None:#if user is connected
            for client in self.current_threads:
                if client[0] == connection:
                    message = f"YOU_ARE_NOW_KICKED|{duration_of_the_kick}"#in seconds
                    client[1].send(message.encode())
                    break

        close_connection(mydb)
        print("[Server_handle kick_user ends]")

    def ban_user(self, user_to_ban):
        print("[Server_handle ban_user starts]")
        print(f"Getting ready to ban a user : {user_to_ban}")

        mydb = establish_connection()

        #first we check if the user exists
        if does_user_exists(mydb, user_to_ban):
            print("This user exists")
        else:
            print("user does not exist")
            return False
        
        #now we gather his data
        user_data = get_user_info(mydb, user_to_ban)

        #Now we set the banned data in banned_users and change auth_user is_banned to 1
        cleaning = update_and_clean_user_data_after_ban(mydb, user_data['id'])
        if cleaning == True:
           print("Success cleaning")
        else:
           print("cleaning not right")

        #here we check if the user is connected and if so fill in his ip right now
        #then send a mess to the client to disconnect him
        connection = None
        for user in self.user_data:
            if user[1]['Username'] == user_to_ban:
                connection = user[0]
                break
        
        ip_adddr = None
        if connection is not None:#if user is currently connected
            for client in self.current_threads:
                if client[0] == connection:
                    ip_adddr = client[1].getsockname()[0]
                    break
        
        print(f"IP Adress : {ip_adddr}")

        if connection is not None and ip_adddr is not None: #if the user is connected and we have his ip, then
            update = update_ip_on_banned_user(mydb, user_data['id'], ip_adddr)

            if update == True:
                print("Ip address succesfully linked to the banned user")
            else:
                print("Ip address could not be linked to the banned user")

            for client in self.current_threads:
                if client[0] == connection:
                    client[1].send("YOU_ARE_NOW_BANNED|0".encode())
                    break
                    #this message will, on the client side, disconnect him.

        #now we clean up and delete his associated rights and friends

        close_connection(mydb)
        print("[Server_handle ban_user stops]")
            
    def show_current_clients(self):
        print(f"Total number of clients = {len(self.current_threads)}")
        for clients in self.current_threads:
            print(f"Client - {clients[0]} -> IS LOGGED ? {clients[2]}")
        
        for user in self.user_data:
            print(f"User data : {user}")

    def log_user(self, client_conn, exit_flag):#the parameter is the connection established with the client.
        try:
            print("[Server_handle log_user starts]")
            client_conn[1].send("INIT_LOGIN_PROCESS".encode())

            while client_conn[2] == False and not exit_flag.is_set():
                try:
                    print("waiting for the correct user data loop")
                    client_conn[1].settimeout(1)
                    response = client_conn[1].recv(1024).decode()
                    
                    
                    print(f"response from {client_conn[0]} : {response}")

                    if response == "/login":
                        print("since response is login, this isn't the user's first try, waiting for data")
                        client_conn[1].send("LOGIN_PROCESS|OK_FOR_RETRY".encode())
                        continue

                    mydb = establish_connection()#Here we check if user exists,

                    user_data_proposed = response.split("|")

                    if does_user_exists(mydb, user_data_proposed[0]):
                        #Then we actually check if his credentials are OK
                        user_data_from_db = get_user_info(mydb, user_data_proposed[0])

                        #if user is banned, we abandon the procedure and disconnect him
                        if user_data_from_db['is_banned'] == 1:
                            kick_or_ban = check_kick_or_ban(mydb, user_data_from_db['id'])
                            if kick_or_ban[0] == True:
                                if kick_or_ban[1] == "KICK":
                                    #IF KICK ->
                                    print("CHECKING IF TIMEOUT OF USER IS OVER OR NOT")
                                    ok_date = kick_or_ban[2][0]#ok-date raw from db
                                    formatted_date = ok_date.strftime('%Y-%m-%d %H:%M:%S')#ok-date formatted for human readability
                                    formatted_date_datetime = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')#ok-date switched to datetime object for comparison
                                    
                                    print(f"OK DATE : {ok_date}")
                                    print(f"USER WAS KICKED UNTIL : {formatted_date}")

                                    current_date = datetime.now()
                                
                                    if current_date > formatted_date_datetime:
                                        print("User should now be able to rejoin the app")

                                        unkick = remove_kick_for_user(mydb, user_data_from_db['id'])
                                        if unkick[0] == True:
                                            print("User has been unkicked.")
                                            pass
                                        else:
                                            print("Could not remove data from previous kick..")
                                            print(f"Error = {unkick[1]}")
                                    else:
                                        print("User CANNOT rejoin the app right now")
                                        message = f"LOGIN_PROCESS_STEP_2_USER_KICKED|{formatted_date}"
                                        client_conn[1].send(message.encode())
                                        try:
                                            self.disconnect_and_clear_client(client_conn[0])
                                        except:
                                            pass
                                        return
                                    pass
                                elif kick_or_ban[1] == "BAN":
                                    #IF BAN ->
                                    print("CANT LOG THIS USER, HE IS BANNED")

                                    conn_ip = client_conn[1].getsockname()[0]
                                    update = update_ip_on_banned_user(mydb, user_data_from_db['id'], conn_ip)

                                    if update == True:
                                        print("Ip adress added to the banned users")
                                    else:
                                        print("could not set user ip adress")

                                    client_conn[1].send("LOGIN_PROCESS_STEP_2_USER_BANNED".encode())

                                    self.disconnect_and_clear_client(client_conn[0])
                                    break
                            else:
                                print(f"Could not reliably determine the user's status (ban or kick), error : \n\n{kick_or_ban[1]}")

                        #print(f"gathered data from db : {user_data_from_db}")
                        if user_data_proposed[1] == user_data_from_db['Password']:
                            
                            print(f"User data from db for user {user_data_from_db['Username']} : {user_data_from_db}")
                            
                            #HERE GATHER ALL THE INFO FROM THE USER BEFORE SENDING IT

                            
                            user_friends = get_user_friends(mydb, user_data_from_db['id'])
                            print(f"USER FRIENDS -> {user_friends}")

                            packet = "LOGIN_PROCESS_STEP_2_OK|"

                            packet = packet + f"{user_data_from_db['id']}/{user_data_from_db['Username']}/{user_data_from_db['First_name']}/{user_data_from_db['Last_name']}/{user_data_from_db['Password']}/{user_data_from_db['Mail']}/{user_data_from_db['User_type']}/{user_data_from_db['is_banned']}/{user_data_from_db['is_connected']}|"

                            for friends in user_friends:
                                friend_info = get_user_info_from_uid(mydb, friends[2])

                                packet = packet + f"{friends[2]}"+ "§" + f"{friend_info['Username']}" + "/"

                            
                            Rooms = get_all_rooms(mydb)
                            print(f"Rooms available : {Rooms}")
                            
                            packet = packet + "|"

                            for room in Rooms:
                                packet = packet + f"{room[0]}-{room[1]}-{room[2]}/"


                            user_rooms_rights = get_user_rooms_rights(mydb, user_data_from_db['id'])

                            print(f"User room rights : {user_rooms_rights}")

                            packet = packet + "|"

                            for rights in user_rooms_rights:
                                packet = packet + f"{rights[0]}-{rights[1]}-{rights[2]}-{rights[3]}/"

                            print(f"PACKET TO SEND : {packet}")

                            client_conn[1].send(packet.encode())


                            ack_complete_log = client_conn[1].recv(1024).decode()
                            if ack_complete_log == "LOGIN_ACK_DONE":
                                #Adding to connection a "connection[2]" containing wether the client is logged or not.
                                client_conn[2] = True
                                #adding the user info to its associated connection.
                                self.user_data.append([client_conn[0], user_data_from_db])

                                print(f"\n\nConnection '{client_conn[0]}' is now logged in.")
                                for client in self.user_data:
                                    if client[0] == client_conn[0]:
                                        print(f"Associated user data : {client[1]}")

                                close_connection(mydb)
                                print("[Server_handle log_user ends]")

                                #once user is fully logged, we setup a listener in the main loop to interact with him
                                main_loop_user = threading.Thread (target=self.listen_to_user, name=client_conn[0], args=(client_conn, exit_flag))
                                main_loop_user.start()
                                return
                        else:
                            print(f"User sent password is not right -> expected : {user_data_from_db['Password']}, received : {user_data_proposed[1]}")
                            client_conn[1].send("LOGIN_PROCESS_STEP_2|NOK|WRONG_PASSWORD".encode())
                    else:
                        print(f"User sent does not exist -> {user_data_proposed[0]}")
                        client_conn[1].send("LOGIN_PROCESS_STEP_2|NOK|USER_DOES_NOT_EXIST".encode())
                except socket.timeout:
                    print("timeout")
        except BrokenPipeError as E:
            display_error("The client has disconnected. Taking him of the current_threads list.\n\n", E)
            self.disconnect_and_clear_client(client_conn[0])
    
    def register_user(self, client_conn, exit_flag):
        print("[Server_handle register_user starts]")
        try:
            #tell the client we are ready to register him up
            client_conn[1].send("INIT_REGISTER_PROCESS".encode())

            while client_conn[2] == False and not exit_flag.is_set():
                try:
                    print("Waiting for the client to send the data")

                    client_conn[1].settimeout(1)
                    response = client_conn[1].recv(1024).decode()

                    response_unpacked = response.split('|')

                    print(f"response from {client_conn[0]} : {response_unpacked}")

                    if response == "/register":
                        print("since response is /register, this isn't the user's first try, waiting for data")
                        client_conn[1].send("REGISTER_PROCESS|OK_FOR_RETRY".encode())
                        continue

                    mydb = establish_connection()

                    #Here is where we check if the computer sending the request is using a banned ip adress.
                    #if so, we prevent him from recreating an account

                    banned_IPs = get_banned_IPs(mydb)
                    current_ip = client_conn[1].getsockname()[0]

                    if banned_IPs[0] == True:
                        print(f"Banned ips : {banned_IPs[1]}")
                        for ip in banned_IPs[1]:
                            if ip[0] == current_ip:
                                print("COMPUTER OF A BANNED USER, USER CREATION NOT ALLOWED")

                                client_conn[1].send("REGISTER_PROCESS_STEP_2|NOK|IP_IS_BANNED".encode())
                                self.disconnect_and_clear_client(client_conn[0])
                                return
                    else:
                        print("Error during gathering of banned ips..")
                        print(banned_IPs[1])

                    if does_user_exists(mydb, response_unpacked[0]) != True:#if user does not already exists.
                        if create_new_user(mydb, response_unpacked):
                            #Adding to connection a "connection[2]" containing wether the client is logged or not.
                            client_conn[2] = True

                            #adding the user info to its associated connection.
                            user_data = get_user_info(mydb, response_unpacked[0])
                            self.user_data.append([client_conn[0], user_data])

                            print(f"\n\nConnection '{client_conn[0]}' is now logged in with their new user account.")
                            for client in self.user_data:
                                    if client[0] == client_conn[0]:
                                        print(f"Associated user data : {client[1]}")

                            
                            rooms = get_all_rooms(mydb)
                            print(f"rooms available : {rooms}")

                            if create_default_user_rooms(mydb, rooms, client[1]['id']):
                                print("Succesfully created default rooms rights for the user.")
                            else:
                                print("Error during default rooms creation.")

                            response_with_UID_and_ROOMS = f"REGISTER_PROCESS_STEP_2_OK|{client[1]['id']}|"
                            for room in rooms:
                                response_with_UID_and_ROOMS = response_with_UID_and_ROOMS + f"{room[0]}-{room[1]}-{room[2]}/"

                            client_conn[1].send(response_with_UID_and_ROOMS.encode())

                            final_client_response = client_conn[1].recv(1024).decode()
                            
                            if final_client_response == "REGISTER_ACK_DONE":
                                print("[Server_handle register_user ends]")
                                close_connection(mydb)
                                main_loop_user = threading.Thread (target=self.listen_to_user, name=client_conn[0], args=(client_conn, exit_flag))
                                main_loop_user.start()
                                return
                        else:
                            client_conn[1].send("REGISTER_PROCESS_STEP_2|NOK|ERROR_WHILE_CREATING_USER".encode())
                    else:
                        client_conn[1].send("REGISTER_PROCESS_STEP_2|NOK|USER_ALREADY_EXISTS".encode())

                except socket.timeout:
                    print("timeout.")
        except BrokenPipeError as E:
            display_error("The client has disconnected. Taking him of the current_threads list.\n\n", E)
            self.disconnect_and_clear_client(client_conn[0])


        print("[Server_handle register_user ends]")
        pass

    def disconnect_and_clear_client(self, client_name):

        for client in self.current_threads:
            if client_name == client[0]:
                for user in self.user_data:
                    if user[0] == client[0]:
                        print(f"deleting user data {user[1]['Username']} from cache")
                        self.user_data.remove(user)

                print(f"deleting user {client[0]} from cache")
                self.current_threads.remove(client)

        print("Items left in self.current_threads :")
        print(self.current_threads)

    def send_broadcast_message(self, message):
        print(len(self.current_threads))
        for client in self.current_threads:
            print(f"sending message for {client[0]}")
            client[1].send(message.encode())

    def send_p2p_message(self, to, connection_from, message):
        print(f"[Server_handle send_p2p_message start]")
        sender = None
        for client in self.user_data:
            if client[0] == connection_from:
                sender = client

        print(f"[Server_handle send_p2p_message FROM {sender[1]['Username']} TO {to} WITH {message} ]")

    def listen_to_user(self, connection, exit_flag):#This can be considered the MAIN LOOP for each client to send messages in.
        print("[Server_handle listen_to_user starts]")
        while not exit_flag.is_set():
            try:
                connection[1].settimeout(3)
                message = connection[1].recv(1024).decode()
                connection[1].settimeout(None)

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
                    elif message_processed[0] == "MESSAGEP2P":
                        #send p2p message with these params : [Target user to send message, connection to use (user sending), content of message]
                        self.send_p2p_message(message_processed[1], connection[0], message_processed[2])
                    elif message_processed[0] == "ROOM_MESSAGE":
                        self.send_message_to_room(message_processed[1], message_processed[2], message_processed[3])
                    elif message_processed[0] == "PRIVATE_MESSAGE":
                        self.send_private_message(message_processed[1], message_processed[2], message_processed[3])
                    elif message_processed[0] == "GATHER_ROOM_MESSAGES":
                        room_data = self.gather_room_data(message_processed[1])
                        

                        packet_length = len(room_data)

                        init_packet = f"READY_FOR_ROOM_DATA|{packet_length}"

                        connection[1].send(init_packet.encode())

                        client_ready = connection[1].recv(1024).decode()

                        if client_ready == "OK_FOR_RECEIVING":
                            for i in range(len(room_data)):
                                single_message = f"FOLLOW_UP_ROOM|{room_data[i][0]}§{room_data[i][1]}§{room_data[i][2]}§{room_data[i][3]}"
                                print(f"Single message sent : {single_message}")
                                connection[1].send(single_message.encode())
                                ACK_response = connection[1].recv(1024).decode()
                                if ACK_response == "OK_FOR_THE_REST":
                                    pass
                            print("Done sending room data..")
                    elif message_processed[0] == "USER_QUERY_FOR_ROOM_RIGHTS":
                        print(f"Data = {message_processed[1]}")
                        print("Submitting rights change for user")
                        room_id = message_processed[1].split("|")[0]
                        UID = message_processed[1].split("|")[1]

                        mydb = establish_connection()
                        result = query_change_room_rights_user(mydb, room_id, UID)
                        close_connection(mydb)
                        
                        if result[0]:#If the function happended with no problem
                            if result[1] == "ACCESS_GRANTED":
                                packet = f"QUERY_ROOM_RIGHTS|ACCESS_GRANTED|{room_id}"
                                connection[1].send(packet.encode())
                            elif result[1] == "ACCESS_ASKED":
                                packet = f"QUERY_ROOM_RIGHTS|PENDING|{room_id}"
                                connection[1].send(packet.encode())
                        else:
                            connection[1].send("QUERY_ROOM_RIGHTS|ERROR_ENCOUNTERED".encode())
                    elif message_processed[0] == "REQUEST_FOR_ADMIN_DEMANDS":
                        print("Starting process to send admin queries data")

                        mydb = establish_connection()
                        result = get_pending_rights(mydb)
                        close_connection(mydb)

                        if result[0]:#If the function happended with no problem
                            demands = result[1]
                            users = result[2]
                            rooms = result[3]
                            demands_assembled = []

                            
                            #now we prepare every single demand with associated user and room name to send one by one to the client
                            for demand in demands:
                                associated_user = None
                                associated_room = None

                                for user in users:
                                    if demand[1] == user[0]:
                                        associated_user = user
                                        break

                                for room in rooms:
                                    if demand[2] == room[0]:
                                        associated_room = room
                                        break

                                demands_assembled.append([demand, associated_user, associated_room])
                                
                            print(f"Assembled demand for sending -> {demands_assembled}")

                            #finally, we can send them one by one, starting by sending the client the len of the packet he's about to receive
                            packet_length = len(demands_assembled)

                            init_packet = f"READY_FOR_PENDING_REQUESTS|{packet_length}"

                            connection[1].send(init_packet.encode())

                            client_ready = connection[1].recv(1024).decode()
                            if client_ready == "OK_FOR_RECEIVING":
                                #send em one by one
                                for i in range(packet_length):##################DEMAND_ID#####################ROOM_NAME####################UID############################USERNAME##################ROOM_ID#############
                                    single_message = f"FOLLOW_UP_DEMAND|{demands_assembled[i][0][0]}§{demands_assembled[i][2][1][0]}§{demands_assembled[i][1][0]}§{demands_assembled[i][1][1][0]}§{demands_assembled[i][2][0]}"
                                    print(single_message)
                                    print(demands_assembled[i])
                                    connection[1].send(single_message.encode())
                                    ACK_response = connection[1].recv(1024).decode()
                                    if ACK_response == "OK_FOR_THE_REST":
                                        pass
                                print("Done sending demands data..")
                        else:
                            connection[1].send("QUERY_PENDING_RIGHTS|ERROR_ENCOUNTERED".encode())
                    elif message_processed[0] == "REQUEST_CHANGE_USER_ROOM_RIGHTS":
                        print("Need to change some room rights for a user")
                        print(f"Data to do so : {message_processed[1]}")

                        demand_id = message_processed[1].split("|")[0]
                        demand_uid = message_processed[1].split("|")[1]
                        new_status = message_processed[1].split("|")[2]

                        print(self.user_data)
                        
                        mydb = establish_connection()
                        result = change_room_right(mydb, demand_id, new_status)
                        close_connection(mydb)

                        print(f"result : {result}")
                        if result[0] == True:
                            print("Access should have been changed")
                            message = f"CHANGING_ROOM_RIGHTS|OK|{demand_id}"#This message is destined to the admin
                            connection[1].send(message.encode()) 

                            #now we check if the user in question is currently connected, if so, we tell him to update his data
                            user_found = False
                            for user in self.user_data:
                                if user[1]['id'] == int(demand_uid) and user_found == False:
                                    connection_to_use = user[0]
                                    for thread in self.current_threads:
                                        if thread[0] == connection_to_use and user_found == False:
                                            if new_status == "OK":
                                                message = f"QUERY_ROOM_RIGHTS|ACCESS_GRANTED|FROM_ADMIN|{demand_id}"
                                                thread[1].send(message.encode())
                                                user_found = True
                                                break
                                            else:
                                                message = f"QUERY_ROOM_RIGHTS|ACCESS_DENIED|FROM_ADMIN|{demand_id}"
                                                thread[1].send(message.encode())
                                                user_found = True
                                                break 
            
                            print("[Server_handle listen_to_user ends]")
                        elif result[0] == False:
                            print("Error during access change")
                            message = f"CHANGING_ROOM_RIGHTS|ERROR"#This message is destined to the admin
                            connection[1].send(message.encode())
                            print("[Server_handle listen_to_user ends]")
                    elif message_processed[0] == "GATHER_PRIVATE_MESSAGES":
                        user_A_id = message_processed[1]
                        user_B_id = message_processed[2]

                        discussion_data = self.gather_discussion_data(user_A_id, user_B_id)

                        packet_length = len(discussion_data)
            
                        init_packet = f"READY_FOR_PRIVATE_DATA|{packet_length}"

                        connection[1].send(init_packet.encode())

                        client_ready = connection[1].recv(1024).decode()
            
                        if client_ready == "OK_FOR_RECEIVING":
                            for i in range(len(discussion_data)):
                                single_message = f"FOLLOW_UP_PRIVATE|{discussion_data[i][0]}§{discussion_data[i][1]}§{discussion_data[i][2]}§{discussion_data[i][3]}"
                                print(f"Single message sent : {single_message}")
                                connection[1].send(single_message.encode())
                                ACK_response = connection[1].recv(1024).decode()
                                if ACK_response == "OK_FOR_THE_REST":
                                    pass
                            print("done sending private data..")
                    else:
                        pass
            except socket.timeout:
                #print("timeout")
                pass   
        else:
            print("FLAG HAS BEEN SET, STOPPING")
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

                print(f"SPlit[0] = {split[0]}")
                match split[0]:
                        case "/broadcast":
                            return ["BROADCAST", split[1]]
                        case "/send":
                            user_to_send = split[1].split(' ')
                            return ["MESSAGEP2P", user_to_send[0], ' '.join(split[1].split()[1:])]
                        case "/room_message":
                            room, UID, *rest_of_string = split[1].split(" ")
                            print(f"Message to send to room {room} with second part {UID} and content {' '.join(rest_of_string)}")
                            return ["ROOM_MESSAGE", room, UID, ' '.join(rest_of_string)]
                        case "/private_message":
                            message_from = split[1].split("|")[0]
                            message_to = split[1].split("|")[1]
                            message = split[1].split("|")[2]
                            return ["PRIVATE_MESSAGE", message_from, message_to, message]
                        case "/need_messages_from_room":
                            room_to_load_from = split[1]
                            return ["GATHER_ROOM_MESSAGES", room_to_load_from]
                        case "/need_messages_from_users":
                            user_A = split[1].split("|")[0]
                            user_B = split[1].split("|")[1]
                            return ["GATHER_PRIVATE_MESSAGES", user_A, user_B]
                        case "/query_for_room_rights":
                            data = split[1]
                            return ["USER_QUERY_FOR_ROOM_RIGHTS", data]
                        case "/request_for_admin_demands":
                            admin_id = split[1]
                            return ["REQUEST_FOR_ADMIN_DEMANDS", admin_id]
                        case "/change_user_room_right":
                            data = split[1]
                            return ["REQUEST_CHANGE_USER_ROOM_RIGHTS", data]
                        case _:
                            return ["", split[1]]
            else: #if command is just a single keyword (ex : /bye  or /logout)
                split = [command]
                match split[0]:
                    case "/bye":
                        return ["BYE", None]
                    case _:
                        return ["SINGLE KEYWORD", None]
        elif case == 2: #If only a random string is sent
            return ["UNKNOWN_CASE_2", None]
        else:
            return ["UNKNOWN", None]
        
    def send_message_to_room(self, room_id, UID, message):
        print("[Server_handle send_message_to_room starts]")

        mydb = establish_connection()
        x = save_message_to_room(mydb, room_id, UID, message)
        if x == 200:
            print("Message succesfully stored in db")
        else:
            print("error while inserting data")
            print(x)

        close_connection(mydb)

        self.update_room_with_new_message(room_id, UID, message)

        print("[Server_handle send_message_to_room ends]")
        
    
    def send_private_message(self, message_from, message_to, message):
        print("[Server_handle send_private_message starts]")

        mydb = establish_connection()
        x = save_private_message(mydb, message_from, message_to, message)
        if x == 200:
            print("Message succesfully stored in db")
        else:
            print("error while inserting data")
            print(x)
        
        close_connection(mydb)

        self.update_user_with_new_message(message_from, message_to, message)

        print("[Server_handle send_private_message ends]")
        

    def update_room_with_new_message(self, room_id, UID_sender, message):
        print("[Server_handle update_room_with_new_message starts]")
        print(f"Message to send to the clients for room {room_id}, from {UID_sender} with message : {message}")
        #print(f"Users data : {self.user_data}")
        #print(f"Current threads : {self.current_threads}")

        asso_UID_sender_connNumber = None
        user_name = None
        
        for user in self.user_data:
            if user[1]['id'] == int(UID_sender):
                asso_UID_sender_connNumber = user[0]
                user_name = user[1]['Username']
            

        print(f"User conn to not send to :\n   ID -> {asso_UID_sender_connNumber}\n   Username -> {user_name}")

        for client in self.current_threads:
            if client[0] != asso_UID_sender_connNumber:#If client is not the one who sent the message
                packet = f"NEW_MESSAGE_ROOM|{room_id}§{user_name}§{message}"

                client[1].send(packet.encode())
        
        
        print("[Server_handle update_room_with_new_message ends]")


    def update_user_with_new_message(self, message_from, message_to, message):
        print("[Server_handle update_user_with_new_message starts]")
        print(f"Message to update for the user {message_to} if he is connected")

        user_name_sender = None
        connNumber_to_send_message = None

        for user in self.user_data:
            if user[1]['id'] == int(message_from):
                user_name_sender = user[1]['Username']
            elif user[1]['id'] == int(message_to):
                connNumber_to_send_message = user[0]
            else:
                pass

        
        if connNumber_to_send_message is not None:#if receiver is connected right now
            packet = f"NEW_PRIVATE_MESSAGE|{message_from}|{user_name_sender}|{message}"

            for client in self.current_threads:
                if client[0] == connNumber_to_send_message:
                    client[1].send(packet.encode())
        else:
            print("User receiving message is not connected, passing.")

        print("[Server_handle update_user_with_new_message ends]")

    def gather_room_data(self, room_id):
        mydb = establish_connection()
        
        result = get_complete_room_data(mydb, room_id)

        close_connection(mydb)

        return result

    def gather_discussion_data(self, user_a_id, user_b_id):
        mydb = establish_connection()

        result = get_complete_private_messages(mydb, user_a_id, user_b_id)

        close_connection(mydb)

        return result
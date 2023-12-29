import socket, threading, os, time
from sys_x import cls
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMainWindow, QComboBox, QMessageBox, QColumnView, QTextEdit, QStatusBar, QMenuBar, QVBoxLayout, QDialog, QScrollArea
from PyQt6.QtCore import QCoreApplication, QRect, QFile, QTextStream, QObject, pyqtSignal, Qt
from PyQt6 import QtCore
from popup import Manage_rooms, Manage_demands, Manage_friends
from functools import partial


class Client_handle(QMainWindow):
    ui_operation_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.logged_in = False #this variable sets to True once client is logged in to the server. use this to prevent actions in case user is not logged.
        self.user_data = None
        self.user_friends = []#contains [friend_uid, friend_name, status]
        self.user_rooms = []
        self.user_rooms_rights = []
        self.current_room = None
        self.current_room_rights = None
        self.listener_for_message_input = False
        self.private_listener_for_message_input = False
        self.ui = None
        self.demands = None
        self.setWindowTitle("LOGIN")  # Set the initial window name
        
        try:
            self.connect_to_server("0.0.0.0", 11111)
            print("[Client_handle INIT connected to server]")
        except Exception as E:
            print("[Client_handle INIT ERROR while connecting to server]")
            print("Please make sure the server is up and running, and on the same subnetwork as you.")
            print(E)
            self.close_application()
            self.terminate_client()
            return

        self.create_login_ui()

        style_file = QFile("styles.css")
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

    def connect_to_server(self, server_IP, server_PORT):
        self.client_socket = socket.socket()
        self.client_socket.connect((server_IP, server_PORT))

    def send_message_server(self, message):
        self.client_socket.send(message.encode())

    def close_application(self):
        QCoreApplication.quit()

    def terminate_client(self):
        # Add any cleanup or termination logic here
        self.client_socket.close()
        os._exit(0)  # Forcefully exit the client process

    def On_log_user_click(self):
        try:
            self.send_message_server("/login")
            self.listen_server_messages_login_register()  #this function is the one that starts the two threads for the client (one for sending one for receiving)
        except BrokenPipeError:
            print("BROCKEN PIPE ERROR, SERVER TURNED OFF, QUITTING.")
            self.terminate_client()
            self.close_application()

    def On_reg_user_click(self):
        self.send_message_server("/register")
        self.listen_server_messages_login_register()  #this function is the one that starts the two threads for the client (one for sending one for receiving)

    def login_process(self):
        #print("[Client_handle login_process starts]")
        while self.logged_in == False:
            #print("loop login_process")

            credentials_username = self.username_input.text()
            credentials_password = self.password_input.text()

            # self.username_input.setReadOnly(True)
            # self.password_input.setReadOnly(True)
            
            user_data = credentials_username + "|" + credentials_password

            self.client_socket.send(user_data.encode())

            server_response = self.client_socket.recv(2048).decode()

            if server_response.split("|")[0] == "LOGIN_PROCESS_STEP_2_OK":
                #print(f"SERVER RESPONSE WITH DATA : {server_response}")

                #Here we take the 2nd part of the server response and
                #update our user_data dictionnary.
                response_user_data = server_response.split("|")[1]
                user_data = {
                    "id": response_user_data.split("/")[0],
                    "Username": response_user_data.split("/")[1],
                    "First_name": response_user_data.split("/")[2],
                    "Last_name": response_user_data.split("/")[3],
                    "Password": response_user_data.split("/")[4],
                    "Mail": response_user_data.split("/")[5],
                    "User_type": response_user_data.split("/")[6],
                    "is_banned": response_user_data.split("/")[7],
                    "is_connected": response_user_data.split("/")[8],
                }
                self.user_data = user_data
                #print(f"Arranged user_data sent from server = {self.user_data}")


                #Here we take the 3rd part of the server response and
                #update the user's friends
                user_friends = server_response.split("|")[2].split("/")
                for users in user_friends:
                    #print(f"Users : {users}")
                    if users != "":
                        friend_uid = users.split("§")[0]
                        friend_username = users.split("§")[1]
                        friend_status = users.split("§")[2]
                        self.user_friends.append([friend_uid, friend_username, friend_status])
                #print(f"friends of the user : {self.user_friends}")


                #here we take the 4th part of the server response and
                #update the user's rooms available
                rooms_available = server_response.split("|")[3].split("/")
                for room in rooms_available:
                    if room != "":
                        self.user_rooms.append([room.split("-")[0], room.split("-")[1], room.split("-")[2]])
                #print(f"Rooms known to the user : {self.user_rooms}")

                

                rooms_rights = server_response.split("|")[4].split("/")
                for room_right in rooms_rights:
                    if room_right != "":
                        self.user_rooms_rights.append([room_right.split("-")[0], room_right.split("-")[1], room_right.split("-")[2], room_right.split("-")[3]])
                #print(f"Rooms rights for the user : {self.user_rooms_rights}")

                #Now we tell the server that the procedure is all done.
                self.client_socket.send("LOGIN_ACK_DONE".encode())
                self.logged_in = True

                #print("[Client_handle login_process ends]")
                self.ui_operation_signal.emit("login success")
                break  # Exit the loop after successful login
            elif server_response == "LOGIN_PROCESS_STEP_2|NOK|USER_DOES_NOT_EXIST":
                self.summon_error_popup("WRONG USER", "This user does not exist. \n\nPlease type in the infos again.\n\nMake sure you are entering the right Username")
                #print("[Client_handle login_process ends]")
                break
                # here send the user back to login asking for creds
            elif server_response == "LOGIN_PROCESS_STEP_2|NOK|WRONG_PASSWORD":
                self.summon_error_popup("WRONG PASSWORD", "The password given is not right. \n\nPlease try again.")
                #print("[Client_handle login_process ends]")
                break
            elif server_response == "LOGIN_PROCESS_STEP_2_USER_BANNED":
                self.summon_error_popup("YOU ARE BANNED", "We cannot log you in because you have been banned from this server.\n\nThe application will now close.")
                self.close_application()
                self.terminate_client()
                
                #print("[Client_handle login_process ends]")
                break
            elif server_response.split("|")[0] == "LOGIN_PROCESS_STEP_2_USER_KICKED":
                ok_date = server_response.split("|")[1]
                self.summon_error_popup("YOU ARE KICKED", f"We cannot log you in because you have been kicked temporarely from this server.\n\nYou can reconnect on the : {ok_date} \n\nThe application will now close.")
                self.close_application()
                self.terminate_client()
    
    def register_process(self):
        #print("[Client_handle register_process starts]")
        
        def verif_new_user_validity(data):
            #Are the two passwords the same ? might as well check here before sending to the server..
            #Add here as elifs any other requirements in the user data form to check.
            
            def has_forbidden_characters(input_string):
                return any(char in {'§', '|', ' '} for char in input_string)
            
            if data['password'] != data['confirmpassword']:
                return "passwords_dont_match"
            elif has_forbidden_characters(data['username']):
                return "unauthorized_caracters_in_username"
            else:    
                return "ok"

        while self.logged_in == False:
            #print("loop register process")

            credentials_username = self.username_input.text()
            credentials_firstname = self.firstname_input.text()
            credentials_lastname = self.lastname_input.text()
            credentials_password = self.password_input.text()
            credentials_confirmpassword = self.confirmpassword_input.text()
            credentials_mail = self.mail_input.text()

            user_data = {
                "username": credentials_username,
                "firstname": credentials_firstname,
                "lastname": credentials_lastname,
                "password": credentials_password,
                "confirmpassword": credentials_confirmpassword,
                "mail": credentials_mail
            }

            check = verif_new_user_validity(user_data)

            if check == "ok":
                #carry on to send the user_data to the server
                #print("User data valid on client-side, sending-it to the server.")

                user_data_packet = user_data['username'] + "|" + user_data['firstname'] + "|" + user_data['lastname'] + "|" + user_data['password'] + "|" + user_data["mail"]

                self.client_socket.send(user_data_packet.encode())

                server_response = self.client_socket.recv(1024).decode()

                if server_response == "REGISTER_PROCESS_STEP_2|NOK|USER_ALREADY_EXISTS":
                    #print("\nThis username is already taken, you need to choose another one..\n\n")
                    self.error_message.setText("This username is already taken, you need to choose another one..")
                    self.grid.addWidget(self.error_message)

                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("USER ALREADY EXISTS")
                    # dlg.setIcon(QMessageBox.warning)
                    dlg.setText("This username is already taken, please choose another one.")
                    dlg.exec()

                    #print("[Client_handle register_process stops]")
                    break
                elif server_response.split("|")[0] == "REGISTER_PROCESS_STEP_2_OK":#IF SERVER CREATED SUCCESFULLY THE USER
                    #Here we update the user data now that the server has created it.

                    self.user_data = {
                        "id": server_response.split("|")[1],
                        "Username": user_data['username'],
                        "First_name": user_data['firstname'],
                        "Last_name": user_data['lastname'],
                        "Password": user_data['password'],
                        "Mail": user_data['mail'],
                        "User_type": "EMPLOYE",
                        "is_banned": 0,
                        "is_connected": "UNDEFINED",
                    }

                    #Here we update the rooms available sent from the server : 
                    
                    user_rooms = server_response.split("|")[2].split("/")
                    for room in user_rooms:
                        if room != '':
                            #print(room)
                            self.user_rooms.append([room.split("-")[0], room.split("-")[1], room.split("-")[2]])

                    #print(f"Rooms available to the user : {self.user_rooms}")

                    #Here we set the default rights to the rooms for a new user
                    self.user_rooms_rights = [[None, self.user_data['id'], '1', 'YES'], [None, self.user_data['id'], '2', 'YES_IF_ASK'], [None, self.user_data['id'], '3', 'NO'], [None, self.user_data['id'], '4', 'NO'], [None, self.user_data['id'], '5', 'NO']]

                    self.client_socket.send("REGISTER_ACK_DONE".encode())
                    self.logged_in = True

                    #print("[Client_handle register_process ends]")
                    self.ui_operation_signal.emit("register success")
                    break
                elif server_response == "REGISTER_PROCESS_STEP_2|NOK|IP_IS_BANNED":
                    self.summon_error_popup("THIS COMPUTER IS BANNED", "This computer has the ip adress of a banned user. \n\nTherefore you will not be allowed to recreate an account here.\n\nPlease see your admin for more informations.\n\n")
                    self.close_application()
                    self.terminate_client()
                    #print("[Client_handle register_process stops]")
                    break
                else:
                    #print(f"server response : {server_response}")
                    break
            elif check == "unauthorized_caracters_in_username":
                cls()
                #print("The username cannot contain special caracters or spaces.")
                self.error_message.setText("The username cannot contain any special caracters or spaces !")
                self.grid.addWidget(self.error_message)

                dlg = QMessageBox(self)
                dlg.setWindowTitle("UNAUTHORISED USERNAME !")
                dlg.setText("The username cannot contain any special caracters or spaces !\n\n")
                dlg.exec()

                break
            else:
                cls()
                #print("The two passwords are not the same, please correct it.")
                self.error_message.setText("The two passwords are not the same, please correct it.")
                self.grid.addWidget(self.error_message)

                dlg = QMessageBox(self)
                dlg.setWindowTitle("PASSWORDS DO NOT MATCH !")
                dlg.setText("The two passwords given do not match, please verify the data entered.")
                dlg.exec()

                break

    def listen_server_messages_login_register(self):
        #print("[Client_handle listen_server_messages_login_register starts]")
        #print(f"Is user logged in : {self.logged_in}")
        while self.logged_in == False:
            #print("loop listen_server_messages_login_register")
            try:
                message = self.client_socket.recv(1024).decode()
                #print(f"Message from server : {message}")

                if message == "INIT_LOGIN_PROCESS" or message == "LOGIN_PROCESS|OK_FOR_RETRY":
                    self.login_process()
                    #print("[Client_handle listen_server_messages_login_register ends]")
                    break
                elif message == "INIT_REGISTER_PROCESS" or message == "REGISTER_PROCESS|OK_FOR_RETRY":
                    self.register_process()
                    #print("[Client_handle listen_server_messages_login_register ends]")
                    break
                elif not message:
                    #print("Server has been disconnected. Please ask your local admin for more informations.")
                    self.terminate_client()
                    self.close_application()
                    self.logged_in = False
                    #print("[Client_handle listen_server_messages_login_register ends]")
                    return
                else:
                    print(f"Message from server: {message}", end='\n   > ', flush=True)
                    #print("[Client_handle listen_server_messages_login_register ends]")
            except Exception as e:
                #print(f"Error: {e}")
                break

    def listen_server(self):#SECONDARY THREAD TO LISTEN TO SERVER (CANT ALTER UI HERE)
        #print("[Client_handle listen_server starts]")

        while self.logged_in == True:
            try:
                message = self.client_socket.recv(4096).decode()

                print(f"Message received from server : {message}")
                
                if not message:
                    #print("The connection to the server has been lost.\nPlease ask your local admin for more informations.")
                    self.summon_error_popup("SERVER DISCONNECTED", "The connection to the server has been lost.\nPlease ask your local admin for more informations.")
                    self.terminate_client()
                    self.close_application()
                    self.logged_in = False
                    #print("[Client_handle listen_server ends]")
                    return
                if message.split("|")[0] == "READY_FOR_ROOM_DATA":
                    #Might need to make this function a thread, this would allow other incoming traffic to be processed. tbd
                    self.client_socket.send("OK_FOR_RECEIVING".encode())

                    for _ in range(int(message.split("|")[1])):
                        single_message = self.client_socket.recv(4096).decode()
                        #print(f"received one mess from a room : {single_message}")

                        self.append_message_to_room(single_message.split("|")[1])

                        time.sleep(0.02)
                        self.client_socket.send("OK_FOR_THE_REST".encode())
                elif message.split("|")[0] == "READY_FOR_PRIVATE_DATA":
                    self.client_socket.send("OK_FOR_RECEIVING".encode())

                    for _ in range(int(message.split("|")[1])):
                        single_message = self.client_socket.recv(4096).decode()
                        #print(f"Received single private message : {single_message}")

                        self.append_message_to_room(single_message.split("|")[1])

                        time.sleep(0.02)
                        self.client_socket.send("OK_FOR_THE_REST".encode())
                elif message.split("|")[0] == "NEW_MESSAGE_ROOM":
                    Room_id = message.split("|")[1].split("§")[0]
                    Username = message.split("|")[1].split("§")[1]
                    Message = message.split("|")[1].split("§")[2]

                    #print(self.current_room)

                    try:
                        if int(self.current_room[0]) == int(Room_id):
                            #print("Adding a new message to the room this client is currently in")
                            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            self.Messages_display.append(f"[{Username} - {formatted_time}] -> {Message}")
                            scroll_bar = self.Messages_display.verticalScrollBar()
                            scroll_bar.setValue(scroll_bar.maximum())
                            pass
                        else:
                            #print("New message received for a room but not the one we're in. \nDiscarding")
                            pass
                    except:
                        #this exception is here in case the current room is not private.
                        pass
                elif message.split("|")[0] == "QUERY_ROOM_RIGHTS":
                    if message.split("|")[1] == "ACCESS_GRANTED":
                        if message.split("|")[2] == "FROM_ADMIN":
                            demand_id = message.split("|")[3]
                            #print(f"Updating the room rights for self.user_rooms_rights where id = {demand_id}")

                            for right in self.user_rooms_rights:
                                if right[0] == demand_id:
                                    right[3] = "YES"
                                    #print(f"User room rights updated")

                            if self.ui is not None:
                                self.ui.ui_operation_signal.emit("destroy")
                            
                            self.ui_operation_signal.emit("NEW_ACCESS_TO_ROOM")
                            #print("[Client_handle listen_server ends]")
                        else:
                            room = int(message.split("|")[2])
                            #print(f"Access to the room {room} has been granted ! Updating the ui now")
                        
                            #First we update the value in self.user_rooms_rights

                            for right in self.user_rooms_rights:
                                if int(right[2]) == room:
                                    right[3] = "YES"
                                    #print(f"User room rights updated")

                            #print("destroy the complete class for Managerooms")
                            self.ui.ui_operation_signal.emit("destroy")
                            #Now we finally restart the main ui
                            self.ui_operation_signal.emit("NEW_ACCESS_TO_ROOM")#This signal not only displays the success message but also regenerates the main ui
                            #print("[Client_handle listen_server ends]")
                    elif message.split("|")[1] == "PENDING":
                        room = int(message.split("|")[2])
                        #print(f"Access to the room {room} is now pending validation from an admin.")

                        #Now we update the value in self.user_rooms_rights
                        for right in self.user_rooms_rights:
                            if int(right[2]) == room:
                                right[3] = "PENDING"
                                #print(f"User room rights updated")
                        
                        #print("regenerate the complete class for Managerooms")
                        #first we destroy the manage rooms window object
                        self.ui.ui_operation_signal.emit("destroy")

                        #then we tell the main ui to restart with manage rooms opened
                        
                        self.ui_operation_signal.emit("ACCESS_TO_ROOM_PENDING")
                        #print("[Client_handle listen_server ends]")
                    elif message.split("|")[1] == "ACCESS_DENIED":
                        demand_id = message.split("|")[3]
                        #print(f"Updating the room rights for self.user_rooms_rights where id = {demand_id}")

                        for right in self.user_rooms_rights:
                                if right[0] == demand_id:
                                    right[3] = "NO"
                                    #print(f"User room rights updated")

                        if self.ui is not None:
                                self.ui.ui_operation_signal.emit("destroy")

                        self.ui_operation_signal.emit("PENDING_RESPONSE_RECEIVED")
                        #print("[Client_handle listen_server ends]")
                elif message.split("|")[0] == "READY_FOR_PENDING_REQUESTS":
                    #Might need to make this function a thread, this would allow other incoming traffic to be processed. tbd
                    self.client_socket.send("OK_FOR_RECEIVING".encode())

                    demands = []
                    for _ in range(int(message.split("|")[1])):
                        single_demand = self.client_socket.recv(1024).decode()
                        #print(f"Received a demand from server : {single_demand}")

                        demand_processed = {
                            "demand_id": single_demand.split("|")[1].split("§")[0],
                            "room_name": single_demand.split("|")[1].split("§")[1],
                            "uid": single_demand.split("|")[1].split("§")[2],
                            "username": single_demand.split("|")[1].split("§")[3],
                            "room_id": single_demand.split("|")[1].split("§")[4]
                        }

                        demands.append(demand_processed)

                        #time.sleep(0.02) No need for the sleep here since we're not doing anything with pyqt (thread handling issues)
                        self.client_socket.send("OK_FOR_THE_REST".encode())
                    
                    #print(f"all demands are ready for display : {demands}")
                    self.demands = demands
                    self.ui_operation_signal.emit("open_admin_demand_window")
                    #print("[Client_handle listen_server ends]")
                    pass
                elif message.split("|")[0] == "CHANGING_ROOM_RIGHTS":#for admin only to use
                    if message.split("|")[1] == "OK":
                        for demand in self.demands:
                            if demand['demand_id'] == message.split("|")[2]:
                                self.demands.remove(demand)
                                break
                        self.ui_operation_signal.emit("reload_admin_demand_window")
                        #print("[Client_handle listen_server ends]")
                    elif message.split("|")[1] == "ERROR":
                        print("ERRROR DURING HANDLE OF USER ROOM DEMAND ON THE SERVER SIDE")
                        #print("[Client_handle listen_server ends]")
                elif message.split("|")[0] == "YOU_ARE_NOW_BANNED":
                    #print("closing this user's app")
                    self.ui_operation_signal.emit("BANNED")
                    time.sleep(5)
                    print("closing app")
                    self.close_application()
                    print("terminate client")
                    self.terminate_client()
                    self.logged_in = False
                    print("Should now be disconnected, check ")
                elif message.split("|")[0] == "SERVER_IS_TURNING_OFF":
                    print("Closing the user's app")
                    self.ui_operation_signal.emit("SERVER_OFF")
                    time.sleep(5)
                    print("closing app")
                    self.close_application()
                    print("terminate client")
                    self.terminate_client()
                    self.logged_in = False
                    print("Should now be disconnected, check ")
                elif message.split("|")[0] == "YOU_ARE_NOW_KICKED":
                    duration = message.split("|")[1]
                    print("closing this user's app")
                    self.ui_operation_signal.emit(f"KICKED|{duration}")
                    time.sleep(5)
                    print("closing app")
                    self.close_application()
                    print("terminate client")
                    self.terminate_client()
                    self.logged_in = False
                    print("Should now be disconnected, check ")
                elif message.split("|")[0] == "NEW_PRIVATE_MESSAGE":
                    message_from = message.split("|")[1]
                    message_from_username = message.split("|")[2]
                    message_content = message.split("|")[3]

                    print(f"Current room : {self.current_room}")
                    try:
                        if int(self.current_room[1]) == int(message_from):#if we are in the discussion with the user we received a mess from
                            print("Adding the message to the current discussion")
                            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            self.Messages_display.append(f"[{message_from_username} - {formatted_time}] -> {message_content}")
                            scroll_bar = self.Messages_display.verticalScrollBar()
                            scroll_bar.setValue(scroll_bar.maximum())
                            pass
                        else:
                            print("New private message received but not talking with the user currently. \nDiscarding")
                            pass
                    except:
                        #this exception is here in case the current room is not private.
                        pass
                elif message.split("|")[0] == "FRIEND_REQUEST":
                    if message.split("|")[1] == "SUCCESS":
                        self.ui_operation_signal.emit("FRIEND_REQUEST_SUCCESS")
                    elif message.split("|")[1] == "SUCCESS_ADMIN":
                        new_friend_id = message.split("|")[2]
                        new_friend_name = message.split("|")[3]
                        self.user_friends.append([new_friend_id, new_friend_name, "OK"])
                        self.ui_operation_signal.emit("FRIEND_REQUEST_SUCCESS_ADMIN")
                    elif message.split("|")[1] == "USER_DOES_NOT_EXISTS":
                        self.ui_operation_signal.emit("friend request to unknown user")
                    elif message.split("|")[1] == "USERS_ARE_ALREADY_FRIENDS":
                        self.ui_operation_signal.emit("users already friends")
                    elif message.split("|")[1] == "USER_ALREADY_SENT_REQUEST":
                        self.ui_operation_signal.emit("user already sent request")
                    elif message.split("|")[1] == "USER_WANTS_TO_BE_FRIEND_ALREADY":
                        self.ui_operation_signal.emit("user can just accept pending demand")
                    else:
                        print("server processing it")
                elif message.split("|")[0] == "UPDATE_FRIEND":
                    if message.split("|")[1] == "UPATE_OK_USERS_ARENT_FRIENDS":
                        print("friend request has been succesfully processed, we can take it off the manage friends window")
                        demand_from = message.split("|")[2]

                        for friend in self.user_friends:#take the request off the user friends known
                            if friend[0] == demand_from:
                                self.user_friends.remove(friend)
                                break
                
                        self.ui_operation_signal.emit("reload manage friends window")
                    elif message.split("|")[1] == "UPATE_OK_USERS_ARE_FRIENDS":
                        print("friend request has been succesfully processed, we can take it off the manage friends window AND add new friend / reload main window")
                        demand_from = message.split("|")[2]
                
                        for friend in self.user_friends:
                            if friend[0] == demand_from:
                                friend[2] = "OK"
                                break
                        
                        self.ui_operation_signal.emit("NEW_FRIEND")
                    elif message.split("|")[1] == "NEW_FRIEND_AVAILABLE":
                        print("A user has accepted one of our friend request, updating UI")
                        friend_to_update = message.split("|")[2]

                        for friend in self.user_friends:
                            if int(friend[0]) == int(friend_to_update):
                                print(f"Updating user {friend[1]} to OK status as friend !")
                                friend[2] = "OK"
                                break
        
                        self.ui_operation_signal.emit("reload ui new friend")
            except Exception as e:
                print(f"Error: {e}")
                self.logged_in = False
                print("[Client_handle listen_server ends]")
                break

    def clear_central_widget(self):
        # Clear the central widget to prepare for a new UI
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.deleteLater()

    def switch_to_register_ui(self):
        self.setWindowTitle("REGISTER")  # Change the window name
        self.clear_central_widget()
        self.create_register_ui()

    def switch_to_login_ui(self):
        self.setWindowTitle("LOGIN")
        self.clear_central_widget()
        self.create_login_ui()

    def create_login_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        self.grid = QGridLayout()
        widget.setLayout(self.grid)

        self.username_label = QLabel("Username : ")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password : ")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Login")
        self.opt_label = QLabel("Don't have an account ?")
        self.register_button = QPushButton("Register")

        widget_list = [
            self.username_label,
            self.username_input,
            self.password_label,
            self.password_input,
            self.login_button,
            self.opt_label,
            self.register_button,
        ]

        for widget in widget_list:
            self.grid.addWidget(widget)


        #the element below is used tto display error messages to the user :
        #therefor, it is not added in the widgets's list straight away
        self.error_message = QLabel()

        self.login_button.clicked.connect(lambda: self.On_log_user_click())
        self.register_button.clicked.connect(self.switch_to_register_ui)

        self.setFixedWidth(300)
        self.setFixedHeight(400) 

        self.grid.setVerticalSpacing(5)
            
    def create_register_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        self.grid = QGridLayout()
        widget.setLayout(self.grid)



        self.username_label = QLabel("Username : ")
        self.username_input = QLineEdit()

        self.firstname_label = QLabel("First name : ")
        self.firstname_input = QLineEdit()

        self.lastname_label = QLabel("Last name : ")
        self.lastname_input = QLineEdit()

        self.mail_label = QLabel("E-mail : ")
        self.mail_input = QLineEdit()

        self.password_label = QLabel("Password : ")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirmpassword_label = QLabel("Confirm password : ")
        self.confirmpassword_input = QLineEdit()
        self.confirmpassword_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("Register")

        self.opt_label = QLabel("Already have an account ?")

        self.login_button = QPushButton("Login")


        widget_list = [
            self.username_label,
            self.username_input,
            self.firstname_label,
            self.firstname_input,
            self.lastname_label,
            self.lastname_input,
            self.mail_label,
            self.mail_input,
            self.password_label,
            self.password_input,
            self.confirmpassword_label,
            self.confirmpassword_input,
            self.register_button,
            self.opt_label,
            self.login_button
        ]

        for widget in widget_list:
            self.grid.addWidget(widget)

        
        self.error_message = QLabel()


        self.register_button.clicked.connect(self.On_reg_user_click)
        self.login_button.clicked.connect(lambda: self.switch_to_login_ui())
        


        self.setFixedWidth(300) #exemple on how to set a window's width and height
        self.setFixedHeight(533)

    def summon_error_popup(self, window_title, Error_message):
        error = QMessageBox(self)
        error.setWindowTitle(window_title)
        error.setText(Error_message)
        error.exec()

    def check_room_right(self, room_name):
        for room in self.user_rooms:
            if room[1] == room_name:
                for right in self.user_rooms_rights:
                    if room[0] == right[2]:
                        if right[3] == "YES":
                            return "YES"
                        elif right[3] == "NO":
                            return "NO"
                        elif right[3] == "YES_IF_ASK":
                            return "YES_IF_ASK"
                        elif right[3] == "PENDING":
                            return "PENDING"

    def on_user_clicked(self, friend_id, friend_name):
        print("[Client_handle on_user_clicked starts]")
        print(f"Start conversation with user : {friend_name} (uid -> {friend_id})")
        self.Messages_display.clear()
        self.Message_input.clear()

        self.current_room = ["PRIVATE_CONV", friend_id, friend_name]
        
        self.Message_input.setEnabled(True)

        self.Main_title.setText(f"Conversation with {friend_name}")

        self.send_message_server(f"/need_messages_from_users {self.user_data['id']}|{friend_id}")

        if self.listener_for_message_input == True:#listener for room messages
            print("an input listener was setup for room messages, taking it off.")
            try:
                self.Send_button.clicked.disconnect(self.send_input_message)
                self.listener_for_message_input = False
            except:
                pass
        else:
            pass

        if self.private_listener_for_message_input == False:
            print("SETTING UP THE MESSAGE INPUT FUNCTION")
            self.Send_button.clicked.connect(self.send_input_private_message)
            self.private_listener_for_message_input = True
        else:
            print("send_input_private_message connect function is already set up, no need to add it again")
        
        print("[Client_handle on_user_clicked ends]")

    def send_input_private_message(self):
        def has_forbidden_characters(input_string):
            return any(char in {'§', '|'} for char in input_string)

        if has_forbidden_characters(self.Message_input.text()):
            print("THIS MESSAGE CONTAINS BANNED CARACTERS, ABORTING")
            self.summon_error_popup("CANNOT SEND SPECIAL CARACTERS", "The message you are trying to send contains banned caracters (§ or |), please remove them before sending the message !\n\n")
            return
        elif len(self.Message_input.text()) > 999:
            print("THIS MESSAGE HAS TOO MANY CARACTERS")
            self.summon_error_popup("MESSAGE TOO LONG", "The message you are trying to send is longer than 1000 caracters, please make the message shorter before sending it !\n\n")
            return

        Message = f"/private_message {self.user_data['id']}|{self.current_room[1]}|{self.Message_input.text()}"
        print(f"Message sent to the server : {Message}")
    
        #Updating the conversation with the message:
        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.Messages_display.append(f"\n[{self.user_data['Username']} - {formatted_time}] -> {self.Message_input.text()}")

        self.Message_input.clear()

        self.send_message_server(Message)

    def send_input_message(self):
        def has_forbidden_characters(input_string):
            return any(char in {'§', '|'} for char in input_string)

        if has_forbidden_characters(self.Message_input.text()):
            print("THIS MESSAGE CONTAINS BANNED CARACTERS, ABORTING")
            self.summon_error_popup("CANNOT SEND SPECIAL CARACTERS", "The message you are trying to send contains banned caracters (§ or |), please remove them before sending the message !\n\n")
            return
        elif len(self.Message_input.text()) > 999:
            print("THIS MESSAGE HAS TOO MANY CARACTERS")
            self.summon_error_popup("MESSAGE TOO LONG", "The message you are trying to send is longer than 1000 caracters, please make the message shorter before sending it !\n\n")
            return
        
        Message = f"/room_message {self.current_room[0]} {self.user_data['id']} {self.Message_input.text()}"
        print(f"Message sent to the server : {Message}")
        
        #Updating the conversation with the message we sent:
        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.Messages_display.append(f"\n[{self.user_data['Username']} - {formatted_time}] -> {self.Message_input.text()}")

        self.Message_input.clear()

        self.send_message_server(Message)

    def create_main_ui(self):
        self.setWindowTitle("CHandler")
        self.setObjectName("CHandler")
        self.resize(1102, 553)
        self.setMinimumSize(QtCore.QSize(1102, 553))
        self.setMaximumSize(QtCore.QSize(1102, 553))

        self.centralwidget = QWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        
        self.Friends_column = QColumnView(self.centralwidget)
        self.Friends_column.setGeometry(QtCore.QRect(0, 0, 221, 511))
        self.Friends_column.setStyleSheet("background-color: #656565;")
        self.Friends_column.setObjectName("Friends_column")

        #Displaying friends to the friends column : 

        self.scroll_area = QScrollArea(self.Friends_column)
        self.scroll_area.setGeometry(0, 0, 221, 430)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_area.setObjectName("SCROLL_AREA_FRIENDS")
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget(self.scroll_area)

        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)

        self.user_buttons = []
        
        color_palette = [["#faf0db", "#dfd7bb"], ["#fbebc7", "#d0c3a7"], ["#fbdfb3", "#ceb793"], ["#f7b886", "#c6956e"], ["#f5b678", "#cf9964"]]#each one [BG color/Border color]
        c = 0
            
        for friend in self.user_friends:
            if friend[2] == "OK":#if friend status is "OK"
                button = QPushButton(friend[1])
                button.setFixedWidth(180)
                button.setStyleSheet(f"background-color: {color_palette[c][0]};\n""color: black;\n"f"border: 2px solid {color_palette[c][1]};")

                self.user_buttons.append([button, friend[0], friend[1]])
                self.scroll_layout.addWidget(button)

                self.scroll_layout.addSpacing(12)
        
                if c == 4:
                    c = 0
                else:
                    c += 1


        for button in self.user_buttons:
            button[0].clicked.connect(partial(self.on_user_clicked, button[1], button[2]))

        self.manage_friends = QPushButton(self.centralwidget)
        self.manage_friends.setGeometry(QtCore.QRect(20, 450, 181, 41))
        self.manage_friends.setObjectName("manage_friends")

        self.Rooms_column = QColumnView(self.centralwidget)
        self.Rooms_column.setGeometry(QtCore.QRect(220, 0, 221, 511))
        self.Rooms_column.setStyleSheet("background-color: #737373;")
        self.Rooms_column.setObjectName("Rooms_column")

        self.Rooms_column.raise_()

        #========================CREATE ALL THE ROOMS =================================

        #print("About to create all rooms.")
        #print(f"Rooms available to the user : {self.user_rooms}")
        #print(f"Rooms rights of the user : {self.user_rooms_rights}")

        #change the labels into buttons for interactions !
        #look at marketing for a template

        #CREATING GENERAL ROOM
        self.general_widget = QWidget(self.centralwidget)
        self.general_widget.setGeometry(QtCore.QRect(230, 10, 201, 61))
        self.general_widget.setObjectName("general_widget")


        self.general_widget_button = QPushButton(self.general_widget)
        self.general_widget_button.setGeometry(QtCore.QRect(0, 0, 201, 61))
        self.general_widget_button.setObjectName("general_widget_button")
        self.general_widget_button.setText("Général")

        room_rights = self.check_room_right("Général")
        if room_rights == "YES":
            self.general_widget_button.setStyleSheet("background-color: #00C113;\n""border: 2px solid #019210")
        elif room_rights == "NO":
            self.general_widget_button.setStyleSheet("background-color: #FF0000;")
        elif room_rights == "YES_IF_ASK":
            self.general_widget_button.setStyleSheet("background-color: #D18438;\n""border: 2px solid #af6e2e")
        elif room_rights == "PENDING":
            self.general_widget_button.setStyleSheet("background-color: #247BC2;\n""border: 2px solid #1d5f94")
                            

        self.general_widget.raise_()
        self.general_widget_button.raise_()

        self.general_widget_button.clicked.connect(lambda: self.on_room_widget_clicked(self.user_rooms[0]))

        #CREATING BLABLA ROOM
        self.blabla_widget = QWidget(self.centralwidget)
        self.blabla_widget.setGeometry(QtCore.QRect(230, 81, 201, 61))
        self.blabla_widget.setObjectName("blabla_widget")


        self.blabla_widget_button = QPushButton(self.blabla_widget)
        self.blabla_widget_button.setGeometry(QtCore.QRect(0, 0, 201, 61))
        self.blabla_widget_button.setObjectName("blabla_widget_button")
        self.blabla_widget_button.setText("Blabla")

        room_rights = self.check_room_right("Blabla")
        if room_rights == "YES":
            self.blabla_widget_button.setStyleSheet("background-color: #00C113;\n""border: 2px solid #019210")
        elif room_rights == "NO":
            self.blabla_widget_button.setStyleSheet("background-color: #FF0000;")
        elif room_rights == "YES_IF_ASK":
            self.blabla_widget_button.setStyleSheet("background-color: #D18438;\n""border: 2px solid #af6e2e")
        elif room_rights == "PENDING":
            self.blabla_widget_button.setStyleSheet("background-color: #247BC2;\n""border: 2px solid #1d5f94")
        
        self.blabla_widget.raise_()
        self.blabla_widget_button.raise_()

        self.blabla_widget_button.clicked.connect(lambda: self.on_room_widget_clicked(self.user_rooms[1]))


        #CREATING COMPTA ROOM
        self.compta_widget = QWidget(self.centralwidget)
        self.compta_widget.setGeometry(QtCore.QRect(230, 152, 201, 61))
        self.compta_widget.setObjectName("compta_widget")


        self.compta_widget_button = QPushButton(self.compta_widget)
        self.compta_widget_button.setGeometry(QtCore.QRect(0, 0, 201, 61))
        self.compta_widget_button.setObjectName("compta_widget_button")
        self.compta_widget_button.setText("Comptabilité")

        room_rights = self.check_room_right("Comptabilité")
        if room_rights == "YES":
            self.compta_widget_button.setStyleSheet("background-color: #00C113;\n""border: 2px solid #019210")
        elif room_rights == "NO":
            self.compta_widget_button.setStyleSheet("background-color: #FF0000;")
        elif room_rights == "YES_IF_ASK":
            self.compta_widget_button.setStyleSheet("background-color: #D18438;\n""border: 2px solid #af6e2e")
        elif room_rights == "PENDING":
            self.compta_widget_button.setStyleSheet("background-color: #247BC2;\n""border: 2px solid #1d5f94")
        
        self.compta_widget.raise_()
        self.compta_widget_button.raise_()

        self.compta_widget_button.clicked.connect(lambda: self.on_room_widget_clicked(self.user_rooms[2]))


        #CREATING INFO ROOM
        self.info_widget = QWidget(self.centralwidget)
        self.info_widget.setGeometry(QtCore.QRect(230, 223, 201, 61))
        self.info_widget.setObjectName("info_widget")


        self.info_widget_button = QPushButton(self.info_widget)
        self.info_widget_button.setGeometry(QtCore.QRect(0, 0, 201, 61))
        self.info_widget_button.setObjectName("info_widget_button")
        self.info_widget_button.setText("Informatique")

        room_rights = self.check_room_right("Informatique")
        if room_rights == "YES":
            self.info_widget_button.setStyleSheet("background-color: #00C113;\n""border: 2px solid #019210")
        elif room_rights == "NO":
            self.info_widget_button.setStyleSheet("background-color: #FF0000;")
        elif room_rights == "YES_IF_ASK":
            self.info_widget_button.setStyleSheet("background-color: #D18438;\n""border: 2px solid #af6e2e")
        elif room_rights == "PENDING":
            self.info_widget_button.setStyleSheet("background-color: #247BC2;\n""border: 2px solid #1d5f94")
        
        self.info_widget.raise_()
        self.info_widget_button.raise_()

        self.info_widget_button.clicked.connect(lambda: self.on_room_widget_clicked(self.user_rooms[3]))


        #CREATING MARKETING ROOM
        self.marketing_widget = QWidget(self.centralwidget)
        self.marketing_widget.setGeometry(QtCore.QRect(230, 294, 201, 61))
        self.marketing_widget.setObjectName("marketing_widget")

        self.marketing_widget_button = QPushButton(self.marketing_widget)
        self.marketing_widget_button.setGeometry(0, 0, 201, 61)
        self.marketing_widget_button.setObjectName("marketing_widget_button")
        self.marketing_widget_button.setText("Marketing")

        room_rights = self.check_room_right("Marketing")
        if room_rights == "YES":
            self.marketing_widget_button.setStyleSheet("background-color: #00C113;\n""border: 2px solid #019210")
        elif room_rights == "NO":
            self.marketing_widget_button.setStyleSheet("background-color: #FF0000;")
        elif room_rights == "YES_IF_ASK":
            self.marketing_widget_button.setStyleSheet("background-color: #D18438;\n""border: 2px solid #af6e2e")
        elif room_rights == "PENDING":
            self.marketing_widget_button.setStyleSheet("background-color: #247BC2;\n""border: 2px solid #1d5f94")


        self.marketing_widget.raise_()
        self.marketing_widget_button.raise_()

        self.marketing_widget_button.clicked.connect(lambda: self.on_room_widget_clicked(self.user_rooms[4]))
        
        
        #========================DONE CREATING ALL THE ROOMS =================================


        self.manage_rooms = QPushButton(self.centralwidget)
        self.manage_rooms.setGeometry(QtCore.QRect(240, 450, 181, 41))
        self.manage_rooms.setObjectName("manage_rooms")

        self.main_container = QColumnView(self.centralwidget)
        self.main_container.setGeometry(QtCore.QRect(440, 0, 651, 511))
        self.main_container.setObjectName("main_container")

        self.Message_input = QLineEdit(self.centralwidget)
        self.Message_input.setEnabled(False)
        self.Message_input.setGeometry(QtCore.QRect(455, 455, 531, 41))
        self.Message_input.setStyleSheet("background-color: white;\n""border: 2px solid black; color: black;\n""border-radius: 5px;")
        self.Message_input.setObjectName("Message_input")

        self.Send_button = QPushButton(self.centralwidget)
        self.Send_button.setGeometry(QtCore.QRect(1010, 457, 60, 35))
        self.Send_button.setObjectName("Send_button")

        self.columnView_4 = QColumnView(self.centralwidget)
        self.columnView_4.setGeometry(QtCore.QRect(440, 0, 651, 81))
        self.columnView_4.setStyleSheet("background-color: #d4cbb6;")
        self.columnView_4.setObjectName("columnView_4")

        self.Messages_display = QTextEdit(self.centralwidget)
        self.Messages_display.setGeometry(QtCore.QRect(455, 100, 621, 341))
        self.Messages_display.setStyleSheet("background-color: white;\n""border-radius: 5px;")
        self.Messages_display.setObjectName("Messages_display")
        self.Messages_display.setReadOnly(True)

        self.Main_title = QLabel(self.centralwidget)
        self.Main_title.setGeometry(QtCore.QRect(500, 25, 511, 50))
        self.Main_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.Main_title.setWordWrap(False)
        self.Main_title.setObjectName("Main_title")


        self.Friends_column.raise_()
        self.scroll_area.raise_()
        self.manage_friends.raise_()
        self.manage_rooms.raise_()
        self.main_container.raise_()
        self.Message_input.raise_()
        self.Send_button.raise_()
        self.columnView_4.raise_()
        self.Messages_display.raise_()
        self.Main_title.raise_()

        
        self.statusbar = QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar()
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1102, 22))
        self.menuBar.setObjectName("menuBar")
        self.setMenuBar(self.menuBar)


        _translate = QtCore.QCoreApplication.translate
        self.manage_friends.setText(_translate("MainWindow", "Manage friends"))
        if self.user_data['User_type'] == "ADMIN":
            self.manage_rooms.setText(_translate("MainWindow", "Manage demands"))
        else:
            self.manage_rooms.setText(_translate("MainWindow", "Manage rooms"))
        self.Send_button.setText(_translate("MainWindow", "Send"))
        self.Main_title.setText(_translate("MainWindow", "Welcome to CHandler !"))
        self.Main_title.setStyleSheet("color: black;\n""font-size: 30px;\n""font-weight: bold;")

        QtCore.QMetaObject.connectSlotsByName(self)

        if self.user_data['User_type'] == "ADMIN":
            self.manage_rooms.clicked.connect(self.manage_demands_action)
        else:
            self.manage_rooms.clicked.connect(self.manage_rooms_action)
            
        self.manage_friends.clicked.connect(self.manage_friends_action)
        
    
        # func1 = threading.Thread(target=self.test_func1)
        
        # func2 = threading.Thread(target=self.test_func2)

        # func1.start()
        # func2.start()

        pass

    def on_room_widget_clicked(self, room_object):
        print("[Client_handle on_room_widget_clicked starts]")
        print(f"room {room_object[1]} clicked !")
        self.Messages_display.clear()
        self.Message_input.clear()
        check_rights = self.check_room_right(room_object[1])
        
        if check_rights == "YES":
            print("User has rights for this server.")

            #Now we update the current room to the user's rights
            self.current_room = room_object
            for right in self.user_rooms_rights:
                if int(right[2]) == int(room_object[0]):
                    self.current_room_rights = right
            
            print(self.current_room)
            print(self.current_room_rights)

            self.Message_input.setEnabled(True)
            self.Main_title.setText(f"Salon {room_object[1]}")

            #HERE WE GATHER ALL THE PREVIOUS MESSAGES FROM THIS ROOM : 
            self.send_message_server(f"/need_messages_from_room {room_object[0]}")

            if self.private_listener_for_message_input == True:
                try:
                    self.Send_button.clicked.disconnect(self.send_input_private_message)
                    self.private_listener_for_message_input = False
                except:
                    pass 
            if self.listener_for_message_input == False:
                print("SETTING UP THE MESSAGE INPUT FUNCTION")
                self.Send_button.clicked.connect(self.send_input_message)
                self.listener_for_message_input = True
            else:
                print("send_input_message connect function is already set up, no need to add it again")

            print("[Client_handle on_room_widget_clicked ends]")
        elif check_rights == "NO":
            self.summon_error_popup("User Rights Issue", "You do not have the appropriate rights to join this room.\n\n")
            print("[Client_handle on_general_widget_clicked ends]")
        elif check_rights == "YES_IF_ASK":
            self.summon_error_popup("Need to ask first", "You do not have the appropriate rights to join this room yet.\n\nPlease click on the 'Manage rooms' button.\nThen, ask to join the room, it will update instantly.")
            print("[Client_handle on_general_widget_clicked ends]")
        elif check_rights == "PENDING":
            self.summon_error_popup("Demand is still pending", "You won't be able to join this channel until an admin has accepted your demand.\n\nPlease be patient or contact one.\n\n")
            print("[Client_handle on_general_widget_clicked ends]")

    def request_friend(self, friend_username):
        print(f"Sending a friend request for {friend_username} !")

        if self.user_data['User_type'] == "ADMIN":
            request = f"/friend_request {self.user_data['id']}|{friend_username}|FORCE"
            self.client_socket.send(request.encode())
        else:
            request = f"/friend_request {self.user_data['id']}|{friend_username}|NORMAL"
            self.client_socket.send(request.encode())

    def manage_friends_action(self):
        print("[Client_Handler manage_friends_action start]")
        print(f"Current friends of the user : {self.user_friends}")
        print(f"User data : {self.user_data}")

        self.ui_operation_signal.emit("start friends window")
    
        print("[Client_Handler manage_friends_action ends]")

    def manage_rooms_action(self):
        print("[Client_Handler manage_rooms_action start]")

        #first get current rooms rights for this user

        #Now we create a class representing the popup window to handle rooms
        POPUP = QDialog(self)
        self.ui = Manage_rooms(self.user_rooms, self.user_rooms_rights)
        self.ui.ui_operation_signal.connect(self.ui.perform_ui_operation)
        self.ui.gen_ui(POPUP)
        POPUP.show()

        #this loop matches every button to its corresponding function to execute
        iteration = 1#This can be later updated to gather the value from len(self.user_rooms) when users can create rooms
        for button in self.ui.buttons:
            match iteration:
                case 1:
                    print("User should always have access to general, so no asking")
                case 2:
                    button.clicked.connect(lambda: self.request_access_to_room(2))
                case 3:
                    button.clicked.connect(lambda: self.request_access_to_room(3))
                case 4:
                    button.clicked.connect(lambda: self.request_access_to_room(4))
                case 5:
                    button.clicked.connect(lambda: self.request_access_to_room(5))
            iteration += 1



        print("[Client_Handler manage_rooms_action ends]")

    def manage_demands_action(self):
        print("[Client_Handler manage_demands_action starts]")
        
        request = f"/request_for_admin_demands {self.user_data['id']}"
        self.client_socket.send(request.encode())

        print("[Client_Handler manage_demands_action ends]")

    def request_access_to_room(self, room_id):
        print("[Client_Handler request_access_to_room starts]")
        room = None
        for r in self.user_rooms:
            if int(r[0]) == room_id:
                room = r
                break
            else:
                pass

        # room_rights = None
        # for rr in self.user_rooms_rights:
        #     if int(rr[2]) == room_id:
        #         room_rights = rr
        #         break
        #     else:
        #         pass

        request = f"/query_for_room_rights {room[0]}|{self.user_data['id']}"
        self.client_socket.send(request.encode())
        print("[Client_Handler request_access_to_room ends]")

    def perform_ui_operation(self, operation):#PRIMARY THREAD (ALTER UI HERE)
        
        #print(f"operation : {operation}")
        if operation == "login success":
            #print("We should start the main loop here and close login UI !")

            #print("cleaning window")
            self.clear_central_widget()
            
            #print("now start real ui")
            self.create_main_ui()
 

            self.server_thread = threading.Thread(target=self.listen_server, name="LISTEN_SERVER")

            self.server_thread.start()
        elif operation == "register success":
            print("We should start the main loop here and close login UI !")

            print("cleaning window")
            self.clear_central_widget()

            print("now start real ui")
            self.create_main_ui()

            self.server_thread = threading.Thread(target=self.listen_server, name="LISTEN_SERVER")

            self.server_thread.start()
        elif operation == "NEW_ACCESS_TO_ROOM":
            self.summon_error_popup("NEW ROOM ACCESSIBLE", "A new room is now accessible, the UI will now be restarted.\n\nFeel free to join it and say hi !\n\n")

            self.clear_central_widget()

            self.create_main_ui()
        elif operation == "NEW_FRIEND":        
            self.summon_error_popup("NEW FRIEND", "You now have a new friend, the UI will be restarted to take changes into account.\n\nFeel free to message your new friend to say hi !\n\n")

            popup = True

            try:
                self.ui.ui_operation_signal.emit("destroy")
            except:
                popup = False
            
            self.clear_central_widget()

            self.create_main_ui()
        
            if popup:
                self.ui_operation_signal.emit("start friends window")
        elif operation == "PENDING_RESPONSE_RECEIVED":
            self.summon_error_popup("PENDING DEMAND REVIEWED", "An admin has reviewed one of your demands to join a room and decided not to let you access it.\n\nWe can't provide much more information, feel free to check with your admin to know why.\n\nThe UI will now be restarted taking this into account.\n\n")

            self.clear_central_widget()

            self.create_main_ui()
        elif operation == "ACCESS_TO_ROOM_PENDING":
            self.summon_error_popup("DEMAND SUBMITED !","Your request has been sent to the admin.\n\nThis room will be available as soon as they decide to let you in.\n\nWe will now reload the app to update the data.\n\n")

            self.clear_central_widget()

            self.create_main_ui()

            self.manage_rooms_action()
        elif operation == "open_admin_demand_window":
            POPUP = QDialog(self)
            self.ui = Manage_demands(self.demands)
            self.ui.ui_operation_signal.connect(self.ui.perform_ui_operation)
            self.ui.gen_ui(POPUP)
            POPUP.show()

            print(f"Ready to join buttons with function for data : {self.demands}")

            i = 0
            for liste in self.ui.button_lists:
                print(f"Demand associated : {self.demands[i]}")
                print(f"Demand id : {liste[2]}")

                #liste[0] = ACCEPT BUTTON / liste[1] = DENY BUTTON / liste[2] = demand_id
                demand_id = liste[2]
                demand_uid = liste[3]

                print(f"liste : {liste}")

                liste[0].clicked.connect(partial(self.handle_user_demand, demand_id, demand_uid, "OK"))
                liste[1].clicked.connect(partial(self.handle_user_demand, demand_id, demand_uid, "NOK"))
                i += 1
        elif operation == "reload_admin_demand_window":
            #reload popup window
            self.summon_error_popup("ROOM ACCESS CHANGED !", "The server confirmed the changes made for this user's access.\n\nThis window will now be reloaded with the updated data\n\n")

            self.ui.ui_operation_signal.emit("destroy")

            print("And now we rebuild it with updated values")

            self.ui_operation_signal.emit("open_admin_demand_window")
        elif operation == "BANNED":
            self.summon_error_popup("YOU ARE BANNED", "You have been banned by an admin. \n\nThis application will now be closed, you will never be able to login again.\n\n")
        elif operation == "friend request to unknown user":
            self.summon_error_popup("USER DOES NOT EXIST", "The user you are trying to send a friend request to does not exist.\n\nPlease verify the Username you entered and/or retry.\n\n")
        elif operation == "SERVER_OFF":
            self.summon_error_popup("SERVER IS TURNING OFF", "The server is turning off, you will now be disconnected too.\n\n")
        elif operation == "users already friends":
            self.summon_error_popup("USER IS A FRIEND", "\nThe user you are trying to send a request to is already your friend.\n\nTherefore sending a request does not make sense.\n\n")
        elif operation == "user already sent request":
            self.summon_error_popup("REQUEST ALREADY SENT", "\nYou already sent a friend request to this user.\n\nPlease simply wait for them to accept it.\n\n")
        elif operation == "user can just accept pending demand":
            self.summon_error_popup("USER SENT YOU A REQUEST", "\nThis user already sent you a friend request !\n\nSimply look for the demand in the 'Manage friends' section of the app.\n\n")
        elif operation == "reload manage friends window":
            self.ui.ui_operation_signal.emit("destroy")

            print("now rebuilding manage friends window..")
                    
            self.ui_operation_signal.emit("start friends window")
        elif operation == "start friends window":
            friend_requests = []
            for friend in self.user_friends:
                if friend[2] == "PENDING":
                    friend_requests.append(friend)
                else:
                    pass

            POPUP = QDialog(self)
            self.ui = Manage_friends(friend_requests)
            self.ui.ui_operation_signal.connect(self.ui.perform_ui_operation)
            self.ui.gen_ui(POPUP)
            POPUP.show()

            #setup listener for the form to add a friend
            self.ui.send_button.clicked.connect(lambda: self.request_friend(self.ui.form_input.text()))

            i = 0
            for liste in self.ui.button_lists:
                print(f"friend request associated : {friend_requests[i]}")
                print(f"Request UID : {liste[2]}")
                
                request_from_uid = liste[2]

                print(f"liste : {liste}")
        
                liste[0].clicked.connect(partial(self.handle_friend_request, request_from_uid, "OK"))
                liste[1].clicked.connect(partial(self.handle_friend_request, request_from_uid, "NOK"))

                i += 1
        elif operation == "FRIEND_REQUEST_SUCCESS":
            self.summon_error_popup("FRIEND REQUEST SUBMITTED", "The friend request has well been submitted to the user !\n\n")
        elif operation == "FRIEND_REQUEST_SUCCESS_ADMIN":
            self.summon_error_popup("FRIEND ADDED", "Since you are an admin, the request has been submitted and validated !\n\nYou can now talk with the user.\n\nWe will now reload the main window to take changes into account.\n\n")

            popup = True

            #destroying the popup
            try:
                self.ui.ui_operation_signal.emit("destroy")
            except:
                popup = False
            #clearing main page
            self.clear_central_widget()
            #reloading main page
            self.create_main_ui()
            #reloading popup
            if popup:
                self.ui_operation_signal.emit("start friends window")
        elif operation == "reload ui new friend":
            self.summon_error_popup("YOU HAVE A NEW FRIEND", "You have a new friend, we will now restart the UI to take the changes into account.\n\nFeel free to say hi to them !\n\n")
            
            self.clear_central_widget()

            self.create_main_ui()
        elif operation.split("|")[0] == "KICKED":
            duration = int(operation.split("|")[1])
            duration_in_minutes = duration / 60
            self.summon_error_popup("YOU ARE KICKED", f"You have been kicked by an admin for {duration_in_minutes} minutes.\n\nFor more information, please feel free to ask them.")
        else:
            print("Other message idk")

    def handle_user_demand(self, demand_id, demand_uid, judgement):
        print("[Client_handle handle_user_demand starts]")
        print(f"Processing demand : {demand_id} for uid : {demand_uid} with result {judgement}")
        
        message = f"/change_user_room_right {demand_id}|{demand_uid}|{judgement}"
        self.client_socket.send(message.encode())
        print("[Client_handle handle_user_demand ends]")
    
    def handle_friend_request(self, demand_from, judgement):
        print("[Client_handle handle_friend_request starts]")
        print(f"Processing friend request from {demand_from} with result : {judgement}")

        message = f"/accept_friend_request {demand_from}|{self.user_data['id']}|{judgement}"
        self.client_socket.send(message.encode())
        print("[Client_handle handle_friend_request ends]")

    def append_message_to_room(self, data):
        print("[Client_handle append_message_to_room starts]")
        try:
            print(f"Message data to sort and appen to text area : {data}")

            #print("CURRENT RESOURCE USAGES : \n")
            #print(resource.getrusage(resource.RUSAGE_SELF))
            #thread_list = threading.enumerate()
            #for thread in thread_list:
            #    print(f"Thread ID: {thread.ident}, Name: {thread.name}, is_alive: {thread.is_alive()}")

            username = data.split("§")[1]
            datetime = data.split("§")[2]
            message = data.split("§")[3]

            print("splitting ok")

            try:
                #pdb.set_trace()
                self.Messages_display.append(f"\n[{username} - {datetime}] -> {message}")
                print("append ok")
            except Exception as E:
                print("ERROR DURING APPENDING THE MESSAGE TO THE QTextEdit")
                print(E)
                print("[Client_handle append_message_to_room ends]")
            
            print("[Client_handle append_message_to_room ends]")
        except Exception as E:
            print("ERROR DURING 'append_message_to_room'")
            print(E)

    








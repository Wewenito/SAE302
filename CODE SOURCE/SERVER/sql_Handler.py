import mysql.connector
import time
from datetime import datetime, timedelta


def establish_connection():
    while True:
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="admin",
                password="admin",
                database="SAE302"
            )
            #print("Connection to the database established")
            return mydb
        except mysql.connector.Error as e:
            if isinstance(e, mysql.connector.InterfaceError):
                print("MySQL server has gone away. Reconnecting in 3 seconds..")
                time.sleep(3)

def close_connection(mydb):
    if mydb.is_connected():
        mydb.close()
        #print("Connection to the database closed")

def does_user_exists(mydb, username):
    mycursor = mydb.cursor()

    query = f"SELECT * FROM auth_user WHERE Username = '{username}'"

    mycursor.execute(query)

    user = mycursor.fetchone()

    if user is not None:
        return True
    else:
        return False

def get_user_info(mydb, username):
    try:
        mycursor = mydb.cursor()

        query = f"SELECT * FROM auth_user WHERE Username = '{username}';"

        mycursor.execute(query)

        user = mycursor.fetchone()

        result_user = {
            "id":user[0],
            "Username":user[1],
            "First_name":user[2],
            "Last_name":user[3],
            "Password":user[4],
            "Mail":user[5],
            "User_type":user[6],
            "is_banned":user[7],
            "is_connected":user[8],
        }

        return result_user
    except Exception as E:
        print(E)
        return None

def update_user_as_admin(mydb, username, UID):
    mycursor = mydb.cursor()
    try:
        query = f"UPDATE auth_user SET user_type = 'ADMIN' WHERE Username = '{username}';"
        mycursor.execute(query)
        mydb.commit()

        for i in range(5):
            try:
                query = f"UPDATE user_rooms SET Access = 'YES' WHERE UID = {int(UID)} AND Salon_id = {i + 1};"
                mycursor.execute(query)
                mydb.commit()
            except Exception as E:
                return [False, E]

        return [True]
    except Exception as E:
        return [False, E]

    
def set_new_user_password(mydb, user, new_password):
    mycursor = mydb.cursor()
    try:
        query = f"UPDATE auth_user SET Password = '{new_password}' WHERE Username = '{user}';"
        mycursor.execute(query)
        mydb.commit()
        return [True]
    except Exception as E:
        return [False, E]
        
def get_user_info_from_uid(mydb, UID):
    try:
        mycursor = mydb.cursor()

        query = f"SELECT * FROM auth_user WHERE id = {UID};"

        mycursor.execute(query)

        user = mycursor.fetchone()

        result_user = {
            "id":user[0],
            "Username":user[1],
            "First_name":user[2],
            "Last_name":user[3],
            "Password":user[4],
            "Mail":user[5],
            "User_type":user[6],
            "is_banned":user[7],
            "is_connected":user[8],
        }

        return result_user
    except Exception as E:
        print(E)
        return None

def create_new_user(mydb, user_data):
    mycursor = mydb.cursor()

    try:
        query = f"INSERT INTO auth_user \
            (Username, First_name, Last_name, Password, Mail, user_type, is_banned, is_connected)\
            VALUES ('{user_data[0]}', '{user_data[1]}', '{user_data[2]}', '{user_data[3]}', '{user_data[4]}', 'EMPLOYE', 0, 'UNDEFINED');"
        

        mycursor.execute(query)
        mydb.commit()
        print("[sql_handler.py create_new_user SUCCESFUL]")
        return True
    except Exception as E:
        print("[sql_handler.py create_new_user ERROR]")
        print(E)
        return False
    
def get_user_friends(mydb, UID):
    mycursor = mydb.cursor()

    try:
        query = f"SELECT * FROM user_friends WHERE UID = {UID};"
        
        mycursor.execute(query)

        user_friends = mycursor.fetchall()

        return user_friends

    except Exception as E:
        print("[sql_handler.py get_user_rights_and_friends ERROR]")
        print(E)
        return False

def get_all_rooms(mydb):
    mycursor = mydb.cursor()

    try:
        query = "SELECT * FROM Salons;"
        
        mycursor.execute(query)
        
        Salons = mycursor.fetchall()

        return Salons
    except Exception as E:
        print("[sql_handler.py get_all_rooms ERROR]")
        print(E)
        return False

def create_default_user_rooms(mydb, rooms, user_id):
    mycursor = mydb.cursor()

    try:
        for room in rooms:
            print(f"Room -> {room}")
            if room[1] == "Général":
                query = f"INSERT INTO user_rooms (UID, Salon_id, Access) VALUES ({user_id}, {room[0]}, 'YES');"
                mycursor.execute(query)
                mydb.commit()
            elif room[1] == "Blabla":
                query = f"INSERT INTO user_rooms (UID, Salon_id, Access) VALUES ({user_id}, {room[0]}, 'YES_IF_ASK');"
                mycursor.execute(query)
                mydb.commit()
            else:
                query = f"INSERT INTO user_rooms (UID, Salon_id, Access) VALUES ({user_id}, {room[0]}, 'NO');"
                mycursor.execute(query)
                mydb.commit()


        return True
    except Exception as E:
        print("[sql_handler.py create_default_user_rooms ERROR]")
        print(E)
        return False
    
def get_user_rooms_rights(mydb, user_id):
    mycursor = mydb.cursor()

    try:
        query = f"SELECT * FROM user_rooms WHERE UID = {user_id};"


        mycursor.execute(query)
        result = mycursor.fetchall()
        if result is None:
            return "NO_RIGHTS"

        return result
            
    except Exception as E:
        print("[sql_handler.py get_user_rooms_rights ERROR]")
        print(E)
        return False

def save_message_to_room(mydb, room_id, UID, message):
    print(f"Saving message to room {room_id}, with UID {UID} and message : {message}")
    
    room_to_save_to = None

    match int(room_id):
        case 1:
            room_to_save_to = "MESSAGES_general"
        case 2:
            room_to_save_to = "MESSAGES_blabla"
        case 3:
            room_to_save_to = "MESSAGES_comptabilite"
        case 4:
            room_to_save_to = "MESSAGES_informatique"
        case 5:
            room_to_save_to = "MESSAGES_marketing"
        case _:
            return "ERROR|Room_does_not_exist"
        
    try:
        print(f"saving message to the table {room_to_save_to}")
        mycursor = mydb.cursor()    
        query = f"INSERT INTO {room_to_save_to} (from_user, timestamp, message_content) VALUES (%s, NOW(), %s);"
        values = (int(UID), message)

        mycursor.execute(query, values)
        mydb.commit()
        return 200
    except Exception as E:
        return E

def save_private_message(mydb, message_from, message_to, message):
    print(f"Saving private message, from {message_from} to {message_to} with the message : {message}")

    try:
        mycursor = mydb.cursor()
        query = f"INSERT INTO MESSAGES_P2P (message_from, message_to, timestamp, message_content) VALUES (%s, %s, NOW(), %s);"
        values = (int(message_from), int(message_to), message)

        mycursor.execute(query, values)
        mydb.commit()
        return 200
    except Exception as E:
        return E

def get_complete_room_data(mydb, room_id):
    mycursor = mydb.cursor()

    #first, get the users allowed on this room
    query = f"SELECT UID FROM user_rooms WHERE Salon_id = {int(room_id)};"

    mycursor.execute(query)

    users_on_this_room = mycursor.fetchall()
    #print(f"Users associated to this room : {users_on_this_room}")

    array_user_id_user_name = [] #contains -> [User_id, user_name]

    for users in users_on_this_room:
        query = f"SELECT Username FROM auth_user WHERE id = {users[0]}"
        
        mycursor.execute(query)

        user_name = mycursor.fetchone()
        #print(f"User name associated with UID {users[0]} -> {user_name[0]}")
        array_user_id_user_name.append([users[0], user_name[0]])

    #print(f"here is the complete array for the users using this room : {array_user_id_user_name}")

    #Now we get all the messages and link each one with the time it was sent and the username :

    match int(room_id):
        case 1:
            query = f"SELECT * FROM MESSAGES_general;"
        case 2:
            query = f"SELECT * FROM MESSAGES_blabla;"
        case 3:
            query = f"SELECT * FROM MESSAGES_comptabilite;"
        case 4:
            query = f"SELECT * FROM MESSAGES_informatique;"
        case 5:
            query = f"SELECT * FROM MESSAGES_marketing;"
        case _:
            return False
    
    mycursor.execute(query)
    
    messages = mycursor.fetchall()

    #Now we order those packets a bit better for the display to the client later on :
    messages_ordered = [] # contains [Message_id, User_name, time, message_content]

    for message in messages: #each message has the following content : [message_id, UID, Time it was sent, Message_content]
        user = None
        for users in array_user_id_user_name:
            if users[0] == message[1]:
                user = users[1]

        messages_ordered.append([message[0], user, message[2], message[3]])

    #print(f"Messages ordered = {messages_ordered}")
    return messages_ordered

def get_complete_private_messages(mydb, user_a_id, user_b_id):
    mycursor = mydb.cursor()

    array_user_id_user_name = [] #contains -> [User_id, user_name]

    #first we get the names of both users:
    query = f"SELECT Username FROM auth_user WHERE id = {int(user_a_id)};"
    mycursor.execute(query)
    username = mycursor.fetchone()
    array_user_id_user_name.append([int(user_a_id), username])

    query2 = f"SELECT Username FROM auth_user WHERE id = {int(user_b_id)};"
    mycursor.execute(query2)
    username = mycursor.fetchone()
    array_user_id_user_name.append([int(user_b_id), username])

    #Now we get all the messages involving the two of them:
    query3 = f"SELECT * FROM MESSAGES_P2P WHERE (message_from = {int(user_a_id)} AND message_to = {int(user_b_id)}) OR (message_from = {int(user_b_id)} AND message_to = {int(user_a_id)});"
    mycursor.execute(query3)
    messages = mycursor.fetchall()
    
    messages_ordered = []

    for message in messages:
        user = None
        for users in array_user_id_user_name:
            if users[0] == message[1]:
                user = users[1]

        messages_ordered.append([message[0], user[0], message[3], message[4]])

    return messages_ordered
    
def query_change_room_rights_user(mydb, room_id, UID):
    mycursor = mydb.cursor()
    
    if int(room_id) == 2:
        print("This room does not need admin approval, authorizing it now")
        
        try:
            query = f"UPDATE user_rooms SET Access = 'YES' WHERE UID = {UID} AND Salon_id = {room_id}"
            mycursor.execute(query)
            mydb.commit()

            return [True, "ACCESS_GRANTED"]
        except Exception as E:
            print(E)
            return [False, E]
    else:
        print("This room does need admin approval, therefore, setting the param to 'PENDING'")

        try:
            query = f"UPDATE user_rooms SET Access = 'PENDING' WHERE UID = {UID} AND Salon_id = {room_id}"
            mycursor.execute(query)
            mydb.commit()

            return [True, "ACCESS_ASKED"]
        except Exception as E:
            print(E)
            return [False, E]

def update_friend_request(mydb, demand_from, demand_to, decision):
    mycursor = mydb.cursor()
    print(f"updating friend request from {demand_from} to {demand_to} with decision : {decision}")

    try:
        if decision == "OK":
            query = f"UPDATE user_friends SET status = 'OK' WHERE UID = {int(demand_from)} AND friend_UID = {int(demand_to)};"
            query2 = f"UPDATE user_friends SET status = 'OK' WHERE UID = {int(demand_to)} AND friend_UID = {int(demand_from)};"
            mycursor.execute(query)
            mycursor.execute(query2)
            mydb.commit()

            return [True, "UPATE_OK_USERS_ARE_FRIENDS"]
        else:
            query = f"DELETE FROM user_friends WHERE UID = {int(demand_from)} AND friend_UID = {int(demand_to)};"
            query2 = f"DELETE FROM user_friends WHERE UID = {int(demand_to)} AND friend_UID = {int(demand_from)};"
            mycursor.execute(query)
            mycursor.execute(query2)
            mydb.commit()

            return [True, "UPATE_OK_USERS_ARENT_FRIENDS"]
    except Exception as E:
        return [False, E]

def get_pending_rights(mydb):
    mycursor = mydb.cursor()

    try:
        query = "SELECT * FROM user_rooms WHERE Access = 'PENDING';"
        mycursor.execute(query)
        pending_demands = mycursor.fetchall()

        users_gathered = []
        rooms_gathered = []
        for demand in pending_demands:
            user_already_fetched = False
            room_already_fetched = False
            uid = demand[1]
            rid = demand[2]

            for i in users_gathered:
                if i[0] == uid:
                    user_already_fetched = True

            for z in rooms_gathered:
                if z[0] == rid:
                    room_already_fetched = True

            if user_already_fetched == False:
                query_users = f"SELECT Username FROM auth_user WHERE id = {uid};"
                mycursor.execute(query_users)
                users_gathered.append([uid, mycursor.fetchone()])

            
            if room_already_fetched == False:
                query_rooms = f"SELECT nom FROM Salons WHERE id = {rid};"
                mycursor.execute(query_rooms)
                rooms_gathered.append([rid, mycursor.fetchone()])


        print(pending_demands)
        return [True, pending_demands, users_gathered, rooms_gathered]
    except Exception as E:
        print(E)
        return [False, E]

def change_room_right(mydb, demand_id, new_status):
    mycursor = mydb.cursor()

    try:
        if new_status == "OK":
            query = f"UPDATE user_rooms SET Access = 'YES' WHERE id = {demand_id};"
            mycursor.execute(query)
            mydb.commit()
            return [True]
        elif new_status == "NOK":
            query = f"UPDATE user_rooms SET Access = 'NO' WHERE id = {demand_id};"
            mycursor.execute(query)
            mydb.commit()
            return [True]
        else:
            print("Error : new status is not logical")
            return [False, "Error : new status is not logical"]
    except Exception as E:
        print(f"Error : {E}")
        return [False, E]

def update_and_clean_user_data_after_ban(mydb, UID):
    #Update user is_banned value
    mycursor = mydb.cursor()

    try:
        query = f"UPDATE auth_user SET is_banned = 1 WHERE id = {UID};"
        mycursor.execute(query)
        mydb.commit()

        #Add the data for his ban in banned_users
        #we can't add the ip right now unless user is connected, checking after this
        query2 = f"INSERT INTO banned_users (UID, ban_or_kick) VALUES ({UID}, 'BAN');"
        mycursor.execute(query2)
        mydb.commit()

        #delete_the_friends
        query3 = f"DELETE FROM user_friends WHERE UID = {UID};"
        mycursor.execute(query3)
        mydb.commit()

        #delete_the_room_rights
        query4 = f"DELETE FROM user_rooms WHERE UID = {UID};"
        mycursor.execute(query4)
        mydb.commit()
    
        return True
    except Exception as E:
        return False

def update_ip_on_banned_user(mydb, UID, IP):
    mycursor = mydb.cursor()

    try:
        query = f"UPDATE banned_users SET ip_adress = '{IP}' WHERE UID = {UID};"
        mycursor.execute(query)
        mydb.commit()

        return True
    except Exception as E:
        return False
    
def get_banned_IPs(mydb):
    mycursor = mydb.cursor()

    try:
        query = f"SELECT ip_adress FROM banned_users;"
        mycursor.execute(query)

        result = mycursor.fetchall()

        return [True, result]
    except Exception as E:
        return [False, E]

def set_kick_for_user(mydb, user_to_kick, duration):
    mycursor = mydb.cursor()
    first_kick = True#has user been kicked before

    #first we check if a kick on the user isn't already active
    try:
        query = f"SELECT is_banned FROM auth_user WHERE id = {user_to_kick};"
        mycursor.execute(query)

        result = mycursor.fetchone()

        if result[0] == 1:
            first_kick = False
            query = f"SELECT ban_or_kick FROM banned_users WHERE UID = {user_to_kick};"
            mycursor.execute(query)
            result = mycursor.fetchone()
        
            if result[0] == "BAN":
                return [False, "USER_IS_BANNED"]
    except Exception as E:
        return [False, E]

    try:
        if first_kick == True:

            query = f"UPDATE auth_user SET is_banned = 1 WHERE id = {user_to_kick};"
            mycursor.execute(query)
            mydb.commit()
    
            future_date = datetime.now() + timedelta(seconds=int(duration))

            print(f"Future date : {future_date}")
            print(f"Future date stringyfied : {future_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            query2 = f"INSERT INTO banned_users (UID, ban_or_kick, duration) VALUES ({user_to_kick}, 'KICK', '{future_date.strftime('%Y-%m-%d %H:%M:%S')}');"
            mycursor.execute(query2)
            mydb.commit()
            return [True]
        else:
            #since user has already a kick, we'll add up the new value to it.
            query = f"UPDATE auth_user SET is_banned = 1 WHERE id = {user_to_kick};"
            mycursor.execute(query)
            mydb.commit()
    
            query = f"SELECT duration FROM banned_users WHERE UID = {user_to_kick};"
            mycursor.execute(query)
            duration = mycursor.fetchone()
            duration = duration[0]
        
            future_date = duration + timedelta(seconds=int(duration))

            print(f"Old date : {duration}")
            print(f"Future date : {future_date}")

            query2 = f"INSERT INTO banned_users (UID, ban_or_kick, duration) VALUES ({user_to_kick}, 'KICK', '{future_date.strftime('%Y-%m-%d %H:%M:%S')}');"
            mycursor.execute(query2)
            mydb.commit()
            return [True]
    except Exception as E:
        return [False, E]

def remove_kick_for_user(mydb, user_to_unkick):
    mycursor = mydb.cursor()

    try:
        query = f"DELETE FROM banned_users WHERE UID = {user_to_unkick};"
        mycursor.execute(query)
        mydb.commit()

        query2 = f"UPDATE auth_user SET is_banned = 0 WHERE id = {user_to_unkick};"
        mycursor.execute(query2)
        mydb.commit()

        return [True]
    except Exception as E:
        return [False, E]

def check_kick_or_ban(mydb, UID):
    mycursor = mydb.cursor()

    try:
        query = f"SELECT ban_or_kick FROM banned_users WHERE UID = {UID};"
        mycursor.execute(query)
        kick_or_ban = mycursor.fetchone()
        
        if kick_or_ban[0] is not None:
            if kick_or_ban[0] == "KICK":
                #gathering the ok-date to give to the server
                query = f"SELECT duration FROM banned_users WHERE UID = {UID};"
                mycursor.execute(query)
                duration = mycursor.fetchone()
                return [True, kick_or_ban[0], duration]
            else:
                return [True, kick_or_ban[0]]
        else:
            return [False, "Var kick_or_ban is Null."]
    except Exception as E:
        return [False, E]
    
def set_friend_request(mydb, demand_from, demand_to, user_type):
    mycursor = mydb.cursor()

    print(f"Setting up friend request from {demand_from} to {demand_to} with type : {user_type}")

    try:
        #first we check if a request isn't already pending
        query = f"SELECT * FROM user_friends WHERE UID = {int(demand_from)} AND friend_UID = {int(demand_to)};"
        mycursor.execute(query)
        result = mycursor.fetchone()

        print(f"Result from query = {result}")

        if result is None:#no friend request pending and they are not already friends
            print("Setting the request in the db.")
            if user_type == "FORCE":#if user is admin
                print("User is admin, forcing the request")
                query = f"INSERT INTO user_friends (UID, friend_UID, status) VALUES ({int(demand_from)}, {int(demand_to)}, 'OK');"#On demander side
                query2 = f"INSERT INTO user_friends (UID, friend_UID, status) VALUES ({int(demand_to)}, {int(demand_from)}, 'OK');"#On demandee side
                mycursor.execute(query)
                mycursor.execute(query2)
                mydb.commit()
                return [True]
            else:
                print("User is not admin, submitting a request")
                query = f"INSERT INTO user_friends (UID, friend_UID, status) VALUES ({int(demand_from)}, {int(demand_to)}, 'WAITING');"#On demander side
                query2 = f"INSERT INTO user_friends (UID, friend_UID, status) VALUES ({int(demand_to)}, {int(demand_from)}, 'PENDING');"#On demandee side
                mycursor.execute(query)
                mycursor.execute(query2)
                mydb.commit()
                return [True]
        else:
            if result[3] == "OK":
                return [False, "USERS_ARE_ALREADY_FRIENDS"]
            elif result[3] == "PENDING":
                return [False, "USER_WANTS_TO_BE_FRIEND_ALREADY"]
            elif result[3] == "WAITING":
                return [False, "USER_ALREADY_SENT_REQUEST"]
    except Exception as E:
        return [False, E]

    pass


import mysql.connector
import time


def establish_connection():
    while True:
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="owen",
                password="j38fqt",
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

        query = f"SELECT * FROM auth_user WHERE Username = '{username}'"

        mycursor.execute(query)

        user = mycursor.fetchone()

        result_user = {
            "id":user[0],
            "Username":user[1],
            "First_name":user[2],
            "Last_name":user[3],
            "Password":user[5],
            "Mail":user[4],
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
            VALUES ('{user_data[0]}', '{user_data[1]}', '{user_data[2]}', '{user_data[4]}', '{user_data[3]}', 'EMPLOYE', 0, 'UNDEFINED');"
        

        mycursor.execute(query)
        mydb.commit()
        print("[sql_handler.py create_new_user SUCCESFUL]")
        return True
    except Exception as E:
        print("[sql_handler.py create_new_user ERROR]")
        print(E)
        return False
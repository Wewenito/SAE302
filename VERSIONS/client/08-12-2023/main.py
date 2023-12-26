from client import Client_handle
from sys_x import cls, display_error
import time, threading

def console_start():
    log_or_reg = str(input("Hello and welcome, please type '/login' to start.\n\nYou can also register if you'd like by typing '/register'\n\n->"))

    if log_or_reg.lower() in ["/login", "l", "1", "/l", "/log"]:
        return "login"
    else:
        return "register"

if __name__ == '__main__':
    x = console_start()

    while True:
        try:
            client = Client_handle()
            client.connect_to_server("0.0.0.0", 11111)
            break
        except ConnectionRefusedError as E:
            display_error("Server is most likely not on or unreachable.\nHere below is the error.\n\n", E)
            print("We will attempt to try to connect again every 5 seconds.")
            time.sleep(5)


    if x == "login":
        client.send_message_server("/login")
    elif x == "register":
        client.send_message_server("/register")

    client.listen_server_messages()#this function is the one that starts the two threads for the client (one for sending one for receiving)

    if client.logged_in == True:
        print("client is logged in, start thread to listen again")
    else:
        print("client is not logged in, back to login")


    






from client import Client_handle
from sys_x import cls, display_error
import time, threading, sys
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    Run = True

    while Run:
        print("Start connecting to server")
        try:
            app = QApplication(sys.argv)
            client = Client_handle()
            client.ui_operation_signal.connect(client.perform_ui_operation)
            client.show()
            sys.exit(app.exec())
            break
        except ConnectionRefusedError as E:
            display_error("Server is most likely not on or unreachable.\nHere below is the error.\n\n", E)
            print("We will attempt to try to connect again every 5 seconds.")
            time.sleep(5)

    print("This is the rest of the main file , that alright ??")


    # if client.logged_in == True:
    #     print("client is logged in, start thread to listen again")
    # else:
    #     print("client is not logged in, back to login")


    






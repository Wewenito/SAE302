from client import Client_handle
import threading






if __name__ == '__main__':
    name = str(input("Please enter your name on the server -> "))

    client = Client_handle(name)
    client.connect_to_server("0.0.0.0", 11111)

    client.send_message(client.client_name)

    listen_thread = threading.Thread(target=client.listen_server_messages)
    listen_thread.start()

    while True:
        # Main thread can handle user input
        order = input("> ")
        client.send_message(order)
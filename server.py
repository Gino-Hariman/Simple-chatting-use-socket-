import socket
import select
import threading

HEADER = 10
IP = '192.168.72.2'
FORMAT = 'utf-8'

PORT = 7777

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# FOR RECONNECT
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

clients = {}

print(f'Listening for connetions on {IP}:{PORT}...')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER)

        if not len(message_header):
            return False

        message_length = int(message_header.decode(FORMAT).strip())

        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)

            clients[client_socket] = user

            # print("Welcome to the Chatroom!")
            print(
                f"Accepted new connection from {client_address}:{client_address[1]} username: {user['data'].decode(FORMAT)}")

        else:
            message = receive_message(notified_socket)

            if message is False:
                print(
                    f"Closed connection from {clients[notified_socket]['data'].decode(FORMAT)}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(
                f"Recieved message from {user['data'].decode(FORMAT)}: {message['data'].decode(FORMAT)}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(
                        user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

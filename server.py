import socket
import select
# import tqdm
import base64
import os
import subprocess

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]

clients = {}
print(f'Listening for connections on {IP}:{PORT}...')
history = []


def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            # print("inja cancel shod")
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


def recieve_file(client_socket):
    try:
        received = client_socket.recv(BUFFER_SIZE).decode()
        print("RECEIVED :", received)
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        filetodown = open("ss.Docx", "wb")
        while True:
            print("Receiving")
            data = client_socket.recv(BUFFER_SIZE)
            if data == b"DONE":
                print("Done Receiving.")
                break
            filetodown.write(data)
        filetodown.close()
        # client_socket.send("Thanks for connecting.")
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
    for socket in read_sockets:
        if socket == server_socket:
            client_socket, addr = server_socket.accept()

            user = recieve_message(client_socket)
            if not user:
                continue
            socket_list.append(client_socket)
            clients[client_socket] = user

            print(f"Accepted new connection from {addr[0]}:{addr[1]}"
                  f" username :{user['data'].decode('utf-8')} ")

        else:
            message = recieve_message(socket)
            if not message:
                print(f"Closed connection from {clients[socket]['data'].decode('utf-8')}")
                socket_list.remove(socket)
                del clients[socket]
                continue

            user = clients[socket]

            print(f"Recieved message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            # history.append(message['data'].decode('utf-8').split()[0])
            if message['data'].decode('utf-8').split()[0] == 'send':

                if message['data'].decode('utf-8').split()[1] == '-e':
                    part_one = message['data'].decode('utf-8')[:8]
                    part_two = message['data'].decode('utf-8')[8:]
                    part_two = part_two.encode('ascii')
                    part_two = base64.b64decode(part_two)
                    message['data'] = (part_one + part_two.decode('ascii')).encode('utf-8')

                    history.append(message['data'].decode('utf-8').split()[0:2])
                else:
                    history.append(message['data'].decode('utf-8').split()[0])

                for client_socket in clients:
                    if client_socket != socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'][5:])

            elif message['data'].decode('utf-8').split()[0] == 'history':
                history.append(message['data'].decode('utf-8').split()[0])
                message['data'] = ''
                for h in history:
                    message['data'] += h
                    message['data'] += '\n'
                message['data'] = message['data'].encode('utf-8')
                message['header'] = f"{len(message['data']):<{HEADER_LENGTH}}".encode('utf-8')

                socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            elif message['data'].decode('utf-8').split()[0] == 'exec':
                history.append(message['data'].decode('utf-8').split()[0])
                print(message['data'].decode('utf-8'))
                # answer = os.system(message['data'].decode('utf-8')[5:])
                answer = subprocess.Popen(message['data'].decode('utf-8')[5:], shell=True, stdout=subprocess.PIPE).stdout.read()
                print(answer)
                message['data'] = answer
                message['header'] = f"{len(message['data']):<{HEADER_LENGTH}}".encode('utf-8')

                socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            elif message['data'].decode('utf-8') == "UPLOADING":
                history.append('upload')

                recieve_file(socket)

            # for client_socket in clients:
            #     if client_socket != socket:
            #         client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for socket in exception_sockets:
        socket_list.remove(socket)
        del clients[socket]

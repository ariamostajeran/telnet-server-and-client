import socket
import select
# import tqdm
import base64
import errno
import sys
import os
import smtplib
import ssl
import subprocess
import threading


def client():

    HEADER_LENGTH = 10

    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 1024

    IP = "127.0.0.1"
    PORT = 1234
    tmp_ip = "0.0.0.0"
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for i in range(1, 2000):
        location = (tmp_ip, i)
        result_of_check = a_socket.connect_ex(location)

        if result_of_check == 0:
            print(f"Port {i} is open")

    my_username = input("Username: ")

    def send_email():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("asg.aut.ac.ir", 25))
        recv = s.recv(1024)
        recv = recv.decode()
        print("Message after connection request:" + recv)
        if recv[:3] != '220':
            print('220 reply not received from server.')
        heloCommand = 'HELO Alice\r\n'
        s.send(heloCommand.encode())
        recv1 = s.recv(1024)
        recv1 = recv1.decode()
        print("Message after HeLO command:" + recv1)
        if recv1[:3] != '250':
            print('250 reply not received from server.')
        mailFrom = "MAIL FROM:<ariamostajeran99@gmail.com>\r\n"
        s.send(mailFrom.encode())
        recv2 = s.recv(1024)
        recv2 = recv2.decode()
        print("After MAIL FROM command: " + recv2)
        rcptTo = "RCPT TO:<ariamostajeran@aut.ac.ir>\r\n"
        s.send(rcptTo.encode())
        recv3 = s.recv(1024)
        recv3 = recv3.decode()
        print("After RCPT TO command: " + recv3)
        data = "DATA\r\n"
        s.send(data.encode())
        recv4 = s.recv(1024)
        recv4 = recv4.decode()
        print("After DATA command: " + recv4)
        msg = "\r\n Test email"
        s.send(msg.encode())
        endmsg = "\r\n.\r\n"
        s.send(endmsg.encode())
        recv_msg = s.recv(1024)
        print("Response after sending message body:" + recv_msg.decode())
        quit = "QUIT\r\n"
        s.send(quit.encode())
        recv5 = s.recv(1024)
        print(recv5.decode())
        s.close()

    # send_email()
    history = []

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)

    while True:
        message = input(f'{my_username} > ')

        if message:
            msg_type = message.split()[0]
            # print(msg_type)

            if msg_type == "send":
                if message.split()[1] == "-e":
                    first_part = message[:8]
                    second = message[8:]
                    second = second.encode('ascii')
                    second = base64.b64encode(second)
                    message = first_part + second.decode('ascii')
                    # message = message.encode('utf-8')

            history.append(msg_type)

            if msg_type == "upload":
                message = "UPLOADING"
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

                client_socket.send(message_header + message)
                message = message.decode('utf-8')

                filename = "Doc.docx"
                filesize = os.path.getsize(filename)
                client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

                filetosend = open(filename, "rb")
                data = filetosend.read(BUFFER_SIZE)
                while data:
                    print("sending")
                    client_socket.send(data)
                    data = filetosend.read(BUFFER_SIZE)
                filetosend.close()
                client_socket.send(b"DONE")
                print("Done Sending")
                # print(client_socket.recv(BUFFER_SIZE))
                # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                # with open(filename, "rb") as f:
                #     while True:
                #         bytes_read = f.read(BUFFER_SIZE)
                #         if not bytes_read:
                #             break
                #         client_socket.sendall(bytes_read)
                #         progress.update(len(bytes_read))

            # elif msg_type == "send":
            #     message = message[5:]
            #     message = message.encode('utf-8')
            #     message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            #
            #     client_socket.send(message_header + message)

            # elif msg_type == "history":
            #     message = ''
            #     for h in history:
            #         message += h
            #         message += '\n'
            #     message = message.encode('utf-8')
            #     message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            #
            #     client_socket.send(message_header + message)
            if message != "UPLOADING":
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

                client_socket.send(message_header + message)

        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)

                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print(f'{username} > {message}')

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()


def server():
    import socket
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
                    answer = subprocess.Popen(message['data'].decode('utf-8')[5:], shell=True,
                                              stdout=subprocess.PIPE).stdout.read()
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


if __name__ == '__main__':
    server = threading.Thread(target=server).start()
    client = threading.Thread(target=client).start()

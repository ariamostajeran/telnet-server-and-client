import socket

def client():
    serverName = "192.168.56.1"
    serverPort = 12000
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    sentence = input("send lower case message")
    clientSocket.send(sentence.encode())
    modifiedSentence = clientSocket.recv(1024)
    print("‘FromServer:’", modifiedSentence.decode())
    clientSocket.close()


def server():
    server = "192.168.56.1"
    serverPort = 12000
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((server, serverPort))
    serverSocket.listen(1)
    print(" ‘The server is ready to receive’")
    while True:
        connectionSocket, addr = serverSocket.accept()

        sentence = connectionSocket.recv(1024).decode()
        capitalizedSentence = sentence.upper()
        connectionSocket.send(capitalizedSentence.
                              encode())
        connectionSocket.close()


# server()
client()    
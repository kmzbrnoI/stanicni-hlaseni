#!/usr/bin/python3 
import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()

port = 9999
serversocket.bind((host, port))
serversocket.listen(1)

print("Nasloucham na portu: ", port);

clientsocket, addr = serversocket.accept()
print("Navazano spojeni %s" % str(addr))
while True:
    try:
        message = input("Zadejte data pro odeslani: ")
        clientsocket.send(message.encode('UTF-8'))
        if message == "ukoncit":
            print("Spojeni bylo ukonceno prikazem...")
            break
    except (KeyboardInterrupt, EOFError):
        clientsocket.send(("ukoncit").encode('UTF-8'))
        break

clientsocket.close()

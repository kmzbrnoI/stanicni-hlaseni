#!/usr/bin/python3 
import socket


def tcp_listener():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = socket.gethostname()

    port = 5896
    serversocket.bind((host, port))
    serversocket.listen(1)

    print("Nasloucham na portu: ", port);

    clientsocket, addr = serversocket.accept()
    print("Navazano spojeni %s" % str(addr))
    message = "hello"
    clientsocket.send(message.encode('UTF-8'))
    while True:
        try:
            input("Zadejte data pro odeslani: ")
            message = "Zd;SH;ODJEDE;{504351;Os;7b;Zd;Klb}"
            clientsocket.send(message.encode('UTF-8'))
            if message == "ukoncit":
                print("Spojeni bylo ukonceno prikazem...")
                break
        except (KeyboardInterrupt, EOFError):
            clientsocket.send(("ukoncit").encode('UTF-8'))
            break

    clientsocket.close()


def udp_listener():
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind(('', 5889))

    while True:
        data, addr = sock.recvfrom(4096)  # buffer size is 1024 bytes
        print(data)
        name = "hJOP;1.0;panel;"
        if str(name) in str(data):
            break


def udp_broadcast(data):
    brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:
        data_to_send = data.encode()
        brd_socket.sendto(data_to_send, ('<broadcast>', 5880))
        break


udp_listener()
udp_broadcast("hJOP;1.0;server;server H0;10.30.137.10;5823;on;MujServer")
tcp_listener()

#!/usr/bin/python3

"""
This is a simple hJOPserver emulator.
"""

import socket


def get_example_message(x):
    if x == 0:
        return input() + '\n'

    return {
        1: 'Ku;SH;PRIJEDE;{501520;MOs;2;Br;Ku;;}',
        2: 'Ku;SH;ODJEDE;{504220;Os;2;Bs;Zd;;}',
        3: 'Ku;SH;SPEC;[NESAHAT]',
        4: 'Ku;SH;CHANGE-SET;{Veronika}',
        5: "PING;"
    }.get(x) + '\n'


def tcp_listener():
    area = "Ku"

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = socket.gethostbyname(socket.gethostname())

    port = 5896
    serversocket.bind(('0.0.0.0', port))
    serversocket.listen(1)

    print("Nasloucham na portu:", port)

    udp_broadcast("hJOP;1.0;server;hJOPserver;" + get_ip() + ";5896;on;modulovka TT")

    clientsocket, addr = serversocket.accept()
    print("Navazano spojeni {0}".format(addr))

    registered = False
    while not registered:
        message = clientsocket.recv(1024).decode('utf-8').strip()
        print("Received:", message)

        if "HELLO" in message:
            hello_msg = "-;HELLO;1.0\n"
            clientsocket.send(hello_msg.encode('UTF-8'))

        elif "SH;REGISTER" in message:
            register_msg = area + ";SH;REGISTER-RESPONSE;OK;\n"
            clientsocket.send(register_msg.encode('UTF-8'))
            registered = True

    while True:
        try:
            print("Zadejte typ zpravy k odeslani:\n"
                  "0 : VLASTNI ZPRAVA\n1 : PRIJEDE\n2 : ODJEDE\n3 : NESAHAT")
            message_type = input()
            message = get_example_message(int(message_type))
            print("Sending:", message)

            clientsocket.send(message.encode('UTF-8'))
            if message == "ukoncit":
                print("Spojeni bylo ukonceno prikazem...")
                break
        except (KeyboardInterrupt, EOFError):
            clientsocket.send("ukoncit".encode('UTF-8'))
            break

        except (KeyboardInterrupt, EOFError):
            clientsocket.send("ukoncit".encode('UTF-8'))
            break

    clientsocket.close()


def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 5880))

    while True:
        data, addr = sock.recvfrom(4096)
        print("UDP_listener: {0}".format(data.decode('utf-8').strip()))
        if "hJOP;1.0;sh;" in str(data):
            return


def udp_broadcast(data):
    brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data_to_send = data.encode('utf-8')
    brd_socket.sendto(data_to_send, ('<broadcast>', 5880))

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

udp_listener()
tcp_listener()

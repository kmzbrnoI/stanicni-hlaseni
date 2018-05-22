#!/usr/bin/python3 
import socket


def get_example_message(x):
    return {
        '1': 'Ku;SH;PRIJEDE;{501520;MOs;1;Br;Bs;;}\n',
        '2': 'Ku;SH;ODJEDE;{504220;Os;1;Bs;Zd;;}\n',
        '3': 'Ku;SH;SPEC;[NESAHAT]\n'
    }.get(x, 'Ku;SH;ODJEDE;{504220;Os;1;Bs;Zd;;}\n')


def tcp_listener():
    area = "Ku"

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = socket.gethostbyname(socket.gethostname())

    port = 5896
    serversocket.bind((host, port))
    serversocket.listen(1)

    print("Nasloucham na portu: ", port);

    clientsocket, addr = serversocket.accept()
    print("Navazano spojeni {0}".format(addr))
    hello_msg = "-;HELLO;1.0\n"

    while True:
        message = clientsocket.recv(1024)
        decoded_message = message.decode("UTF-8")
        print("message: ", message)

        if "HELLO" in str(message):
            hello_msg = "-;HELLO;1.0\n"
            clientsocket.send(hello_msg.encode('UTF-8'))

        elif "SH;REGISTER" in message.decode('UTF-8'):
            register_msg = area + ";SH;REGISTER-RESPONSE;OK;\n"
            clientsocket.send(register_msg.encode('UTF-8'))
            break

        else:
            ping_msg = "PING;\n"
            clientsocket.send(ping_msg.encode('UTF-8'))

    while True:
        try:
            message = ""
            print("Zadejte typ zpravy, ktery se odesle.\n1 : PRIJEDE\n2 : ODJEDE\n3 : NESAHAT ")
            type = input()
            message = get_example_message(type)
            print("zprava: ", message)
            
            clientsocket.send(message.encode('UTF-8'))
            if message == "ukoncit":
                print("Spojeni bylo ukonceno prikazem...")
                break
        except (KeyboardInterrupt, EOFError):
            clientsocket.send(("ukoncit").encode('UTF-8'))
            break

        except (KeyboardInterrupt, EOFError):
            clientsocket.send(("ukoncit").encode('UTF-8'))
            break

    clientsocket.close()


def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 5889))

    while True:
        data, addr = sock.recvfrom(4096)
        print("UDP_listener {0}".format(data))
        connected = "hJOP;1.0;panel;"
        if connected in str(data):
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
current_ip = socket.gethostbyname(socket.gethostname())
udp_broadcast("hJOP;1.0;server;server H0;" + current_ip + ";5896;on;hJOPEmulator")
tcp_listener()

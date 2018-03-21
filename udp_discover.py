import socket

import system_functions


class ServerNotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class UDPTimeoutError(socket.timeout):
    pass


def udp_broadcast(port, data):
    broadcast_count = 0
    brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data_to_send = data.encode()
    brd_socket.sendto(data_to_send, ('<broadcast>', port))
    brd_socket.sendto(data_to_send, ('<broadcast>', 5889))  # pouze pro emulaci serveru


def get_ip(name):
    port = 5880;
    # Metoda slouží pro odeslání informací o zařízení (RPI) na server a získání odpovědi skrze broadcast od serveru.
    # print("Spustim UDP listener...")

    for i in range(1, 4):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        udp_broadcast(port, "hJOP;1.0;panel;;" + system_functions.get_device_ip() + ";;;\n")

        s.bind(('', port))
        s.settimeout(5)

        message = ""
        device = ""

        print("Pocet pokusu pro UDP: ", i)

        try:
            message = s.recvfrom(4096)
            # print("Zprava: ", message)

            if message:

                device_info, ip = message

                if name in str(device_info):
                    device = device_info

                if device:

                    server = str(device).split(";")
                    server_ip = server[4]
                    server_port = server[5]

                    return (server_ip, server_port)

                else:
                    raise ServerNotFoundError("Nenalezen server s předaným parametrem")


        except socket.timeout:
            print("Nedosla odpoved na UDP (timeout)")

    raise UDPTimeoutError("UDP Timeout")

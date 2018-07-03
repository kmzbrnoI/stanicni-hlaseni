import logging
import socket
import time

import system_functions


class ServerNotFoundError(Exception):
    pass


class UDPTimeoutError(socket.timeout):
    pass


def udp_broadcast(port, data):
    brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data_to_send = data.encode()
    brd_socket.sendto(data_to_send, ('<broadcast>', port))
    brd_socket.sendto(data_to_send, ('<broadcast>', 5889))  # pouze pro emulaci serveru


def get_ip(name):
    port = 5880
    # Metoda slouží pro odeslání informací o zařízení (RPI) na server a získání odpovědi skrze broadcast od serveru.

    for _ in range(3):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        udp_broadcast(port, "hJOP;1.0;panel;;" + system_functions.get_device_ip() + ";;;\n")

        s.bind(('', port))
        s.settimeout(5)

        device = ""

        logging.debug("Pocet pokusu pro UDP: {0}".format(_ + 1))

        try:
            message = s.recvfrom(4096)

            if message:

                device_info, ip = message

                logging.debug("Na UDP odpovedel server: {0}".format(device_info))

                if name in str(device_info):
                    device = device_info

                if device:
                    logging.debug("Nalezen server: {0}".format(device))

                    server = str(device).split(";")
                    server_ip = server[4]
                    server_port = server[5]
                    is_on = server[6]
                    if "on" in is_on:
                        return server_ip, server_port
                    else:
                        break

        except socket.timeout:
            logging.error("Nedosla odpoved na UDP (timeout)")

        except IOError as e:
            logging.error("Nedosla odpoved na UDP (timeout) {0}".format(e))
            time.sleep(30)

        except ServerNotFoundError(Exception):
            logging.error("Server nenalezen...")

    raise ServerNotFoundError("Server nenalezen...")

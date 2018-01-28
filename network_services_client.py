#!/usr/bin/python3

import socket
import time
import report_manager


class NetworkServicesClient():
    def __init__(self):
        self.connection_attempts = 0
        self.communication_accomplished = False
        self.broadcast_port = 0

    def get_connection_attempts(self):
        return self.connection_attempts

    def add_connection_attempts(self):
        self.connection_attempts += 1

    def udp_broadcast(self, port, data):
        broadcast_count = 0
        brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        brd_socket.bind(('', 0))
        brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            data_to_send = data.encode()  # nahradit podle parametru pro HJOP
            self.broadcast_port = port
            brd_socket.sendto(data_to_send, ('<broadcast>', port))
            time.sleep(1)
            broadcast_count += 1
            if broadcast_count > 2:
                brd_socket.close()
                break

    def udp_listener(self, port):
        print("Nasloucham...")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # port = self.broadcast_port
        s.bind(('', port))
        while (1):
            message = s.recvfrom(4096)
            print(message)
            return message

    def tcp_listener(self, port):
        try:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = socket.gethostname()
            while (self.communication_accomplished == False) and (self.get_connection_attempts() < 5):
                self.add_connection_attempts()

                try:
                    clientsocket.connect((host, port))
                    self.communication_accomplished = True
                except socket.error:
                    print("Server neni zapnuty!")
                    print("Pocet pokusu: ", self.get_connection_attempts())
                    time.sleep(5)
                    if self.get_connection_attempts() >= 5:
                        print("Ukoncuji spojeni")
                        break;
                    self.tcp_listener(port)

            if (self.communication_accomplished):
                print("Zarizeni je pripraveno k prijmu dat...")
                message = ""
                while True:
                    try:
                        message = clientsocket.recv(1024)
                        decoded_message = message.decode('UTF-8')
                        if decoded_message == "ukoncit":
                            break
                        report_list = decoded_message.split(" ")
                        report_manager.create_report(report_list, 1)
                        print(message.decode('UTF-8'))
                    except socket.error:
                        print("Nastala chyba pri prijmu dat...")

                # communication_accomplished = False
                print("Server ukoncil spojeni...")
                clientsocket.close()
                print("Ukoncuji tcp_listener...")

            else:
                print("Spojeni se nepovedlo navazat, zarizeni neni pripraveno k prijmu dat...")

        except socket.timeout:
            print("Nepovedlo se navazat spojeni!")
            communication_accomplished = False

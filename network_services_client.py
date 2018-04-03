#!/usr/bin/python3

import socket
import time

import message_parser
import report_manager
import system_functions
import process_message


class TCPCommunicationEstablishedError(socket.error):
    pass


class TCPTimeoutError(socket.timeout):
    pass


class NetworkServicesClient():
    def __init__(self):
        self.rm = report_manager.ReportManager()
        self.device_info = system_functions.DeviceInfo()
        self.server_ip = ""
        self.server_port = ""

    def listen(self, socket):
        while True:
            try:

                message = socket.recv(1024)

                while not message.decode('UTF-8').endswith('\n'):
                    message += socket.recv(1024)

                decoded_message = message.decode('UTF-8')

                if decoded_message == "ukoncit":
                    break

                if "-;PING" in decoded_message:
                    continue

                if 'SH' in decoded_message:
                    
                    process_message.process_message([decoded_message])

            except socket.error:
                print("Nastala chyba pri prijmu dat...")

            except socket.timeout:
                print("TCP Timeout")

    def connect(self, ip, port):

        try:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            clientsocket.settimeout(20)
            clientsocket.connect((ip, port))
            clientsocket.send("-;HELLO;1.0\n".encode('UTF-8'))

            message = clientsocket.recv(1024)
            decoded_message = str(message.decode('UTF-8'))

           
            if 'hello' in decoded_message.lower() : #muze se stat, ze zrovna prijde ping
                
                hello_message = message_parser.parse(message.decode('UTF-8'), ";")

                version = hello_message[-1]

                version = version.replace("\n", "")
                version = version.replace("\r", "")

                version = float(version)

                print("Verze hello: ", version)

                return (clientsocket, version)


        except socket.error:
            # raise TCPCommunicationEstablishedError("Server neni zapnuty!")
            print("Nepodarilo se navazat komunikaci se serverem Error")

        except socket.timeout:
            print("TCP Timeout")
            # raise TCPTimeoutError("TCP Timeout")

    def register_device(self, socket):
        register_message = self.device_info.area + ";SH;REGISTER\n";
        socket.send(register_message.encode('UTF-8'))  # musím na server odeslat registrační zprávu

        message = socket.recv(1024)

        while not message.decode('UTF-8').endswith('\n'):
            message += clientsocket.recv(1024)

        decoded_message = message.decode('UTF-8')

        if decoded_message:  # tady potom přidat try, zda OŘ existuje
            return socket

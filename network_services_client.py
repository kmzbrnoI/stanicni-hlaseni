#!/usr/bin/python3

import socket
import time

import message_parser
import report_manager
import system_functions


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
        self.word_list = {'PRIJEDE': 'parts/prijede.ogg', 'ODJEDE': 'parts/odjede.ogg',
                          'Os': 'trainType/osobni_vlak_cislo.ogg',
                          'Ku': 'stations/kurim.ogg', 'Bs': 'stations/veverska_bityska.ogg'}

    def listen(self, socket):
        while True:
            try:

                message = socket.recv(1024)

                while not message.decode('UTF-8').endswith('\n'):
                    message += socket.recv(1024)

                decoded_message = message.decode('UTF-8')

                print(decoded_message)
                if decoded_message == "ukoncit":
                    break

                if decoded_message == "zvuky":
                    system_functions.download_sound_files_samba("10.0.0.32", "share", self.rm.sound_set)
                    continue

                if "-;PING" in decoded_message:
                    continue

                if 'SH' in decoded_message:
                    data = message_parser.parse(decoded_message, ';')

                    print(data)

                    train_number = train_info_list[0]
                    report_list = []

                    report_list.append("salutation/vazeni_cestujici.ogg")
                    report_list.append("salutation/prosim_pozor.ogg")
                    report_list.append(self.word_list[train_info_list[1]])  # osobní vlak, rychlík

                    report_list += self.rm.parse_train_number(train_number)

                    report_list.append(self.word_list[basic_info_list[2]])  # odjede, prijede...

                    self.rm.create_report(report_list)


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

            if message:
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

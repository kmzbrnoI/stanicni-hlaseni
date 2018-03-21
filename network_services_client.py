#!/usr/bin/python3

import socket
import time

import report_manager
import system_functions


class NetworkServicesClient():
    def __init__(self):
        self.connection_attempts = 0
        self.communication_accomplished = False
        self.broadcast_port = 0
        self.rm = report_manager.ReportManager()
        self.device_info = system_functions.DeviceInfo()
        self.server_ip = ""
        self.server_port = ""
        self.word_list = {'PRIJEDE': 'parts/prijede.ogg', 'ODJEDE': 'parts/odjede.ogg',
                          'Os': 'trainType/osobni_vlak_cislo.ogg',
                          'Ku': 'stations/kurim.ogg', 'Bs': 'stations/veverska_bityska.ogg'}

    def get_connection_attempts(self):
        return self.connection_attempts

    def add_connection_attempts(self):
        self.connection_attempts += 1

    def tcp_listener(self, port):
        try:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # host = self.server_ip
            host = socket.gethostname()

            while (not self.communication_accomplished) and (self.get_connection_attempts() < 5):
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
                        break
                    self.tcp_listener(port)

            if (self.communication_accomplished):
                clientsocket.send("-;HELLO;1.0\n".encode('UTF-8'))  # nezapomínat na konec řádku!
                # print("odeslano hello..")
                print("Zarizeni je pripraveno k prijmu dat...")
                message = clientsocket.recv(1024)
                print(message.decode('UTF-8'))  # zkontrolovat verzi
                register_message = self.device_info.area + ";SH;REGISTER\n";
                clientsocket.send(register_message.encode('UTF-8'))  # musím na server odeslat registrační zprávu
                while True:  # funkce listen()
                    try:

                        message = clientsocket.recv(1024)

                        while not message.decode('UTF-8').endswith('\n'):
                            message += clientsocket.recv(1024)

                        decoded_message = message.decode('UTF-8')

                        if decoded_message == "ukoncit":
                            break
                        if decoded_message == "zvuky":
                            system_functions.download_sound_files_samba("10.0.0.32", "share", self.rm.sound_set)
                            continue
                        if decoded_message != "-;PING\r\n":
                            if 'SH' in decoded_message:
                                data_to_read = decoded_message.partition('{')
                                print(data_to_read)
                                # přijatou zprávu rozdělím na časti podle znaku {
                                basic_info = data_to_read[0]
                                train_info = data_to_read[2].partition('}')[0]

                                basic_info_list = basic_info.split(";")
                                # print("Message: ",decoded_message)
                                train_info_list = train_info.split(";")

                                basic_info_list.pop()
                                print("Basic info list:", basic_info_list)
                                print("Train info list: ", train_info_list)

                                """
                                Priklad:
                                Ku;SH;ODJEDE;
                                504220;Os;1;Ku;Bs
                                """

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

                print("Server ukoncil spojeni...")
                clientsocket.close()
                print("Ukoncuji tcp_listener...")

            else:
                print("Spojeni se nepovedlo navazat, zarizeni neni pripraveno k prijmu dat...")

        except socket.timeout:
            print("Nepovedlo se navazat spojeni!")
            communication_accomplished = False

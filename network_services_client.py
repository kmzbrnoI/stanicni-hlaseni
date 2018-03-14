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

    def udp_broadcast(self, port, data):

        broadcast_count = 0
        brd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        brd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            # TODO: Nastavit podminku pro cyklus
            data_to_send = data.encode()
            self.broadcast_port = port
            brd_socket.sendto(data_to_send, ('<broadcast>', port))
            brd_socket.sendto(data_to_send, ('<broadcast>', 5889))  # pouze pro emulaci serveru

            break

    def udp_broadcast_listener(self, port):
        # Metoda slouží pro odeslání informací o zařízení (RPI) na server a získání odpovědi skrze broadcast od serveru.
        # print("Spustim UDP listener...")
        i = 1
        while i <= 3: #prepsat na for
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.udp_broadcast(port, "hJOP;1.0;panel;;" + system_functions.get_device_ip() + ";;;\n")

            s.bind(('', port))
            s.settimeout(20)

            devices = []
            message = ""

            print("Pocet pokusu pro UDP: ", i)

            try:
                message = s.recvfrom(4096)
                print("Zprava: ", message)

                if message:
                    self.device_info.server_name = "server H0"  # jméno serveru se bude číst z configu
                    shorted_message = message
                    if str(self.device_info.server_name) in str(shorted_message): #proc str()?
                        devices.append(message) #staci rozdelit zpravu, kdyz najdu spravny nazev, tak se pripojím na ten spravny
                        # print("pripojeno ", message)

                if devices:
                    # print("Nalezeno spravne zarizeni!")
                    device = devices[0]

                    server = device[1]
                    self.server_ip = server[0]
                    self.server_port = server[1]
                    return True


            except socket.timeout:
                print("UDP timeout...")
                i += 1
                continue

    def tcp_listener(self, port):
        try:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = self.server_ip
            #host = socket.gethostname()

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
                print(message.decode('UTF-8'), end="") #zkontrolovat verzi
                clientsocket.send("Ku;SH;REGISTER\n".encode('UTF-8'))  # musím na server odeslat registrační zprávu -- Ku;SH do device_config
                while True: #funkce listen()
                    try:
                        message = clientsocket.recv(1024) #velikost zpravy, dokud neni konec radku

                        decoded_message = message.decode('UTF-8')
                        #print(decoded_message)
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

#!/usr/bin/python3

import logging
import socket
import threading
import time

import message_parser
import process_message
import report_manager
import system_functions


class TCPCommunicationEstablishedError(socket.error):
    pass


class TCPTimeoutError(socket.timeout):
    pass


class OutdatedVersionError(Exception):
    pass


class NetworkServicesClient:
    def __init__(self):
        self.rm = report_manager.ReportManager()
        self.device_info = system_functions.DeviceInfo()
        self.server_ip = ""
        self.server_port = ""
        self.connection_established = False

    def listen(self, socket):
        message_part = ""
        buffer = []

        while True:
            try:

                message = socket.recv(2048)

                socket.settimeout(60)

                if message_part:
                    # předchozí zpráva došla po částech
                    message = message_part.encode('UTF-8') + message
                    message_part = ""

                while True:
                    # pokud zprava neobsahuje \n přijímám dál...
                    if '\n' in message.decode('UTF-8'):
                        break
                    else:
                        message += socket.recv(2048)

                logging.debug("Prijata zprava: {0}".format(message))
                decoded_message = message.decode('UTF-8')

                buffer += decoded_message.splitlines(True)

                while buffer:

                    if buffer[-1].endswith('\n'):  # vše ok

                        message_to_process = buffer.pop(0)

                        if "-;HELLO" in message_to_process:
                            self.process_hello_response(socket, message_to_process)

                        elif "REGISTER-RESPONSE;" in message_to_process:
                            self.process_register_response(socket, message_to_process)

                        elif ('SH' in message_to_process) and self.connection_established:
                            logging.debug("Zpracovava se: {0}".format(message_to_process))
                            threading.Thread(target=process_message.process_message(message_to_process)).start()

                    else:
                        # vyhodím poslední prvek z bufferu a připojím na začátek nové zprávy
                        message_part = buffer.pop()
                        break

            except Exception:
                logging.warning("TCP Timeout...")
                break

    def send_message(self, socket, message):
        try:
            socket.send(message.encode('UTF-8'))

        except socket.error:
            # raise TCPCommunicationEstablishedError("Server neni zapnuty!")
            logging.error("Nepodarilo se odeslat zpravu na serveru...")

        except socket.timeout:
            logging.warning("TCP Timeout...")
            # raise TCPTimeoutError("TCP Timeout")

    def process_hello_response(self, socket, message):

        hello_message = message_parser.parse(message, ";")
        version = hello_message[-1]
        version = version.replace("\n", "")
        version = version.replace("\r", "")

        version = float(version)

        logging.debug("Verze hello: {0}".format(version))

        if version >= 1:
            register_message = self.device_info.area + ";SH;REGISTER\n"
            self.send_message(socket, register_message)

        else:
            raise OutdatedVersionError("Je potreba aktualizovat verzi..")

    def process_register_response(self, socket, message):
        register_response = message_parser.parse(message, ";")

        state = register_response[3]

        state = state.replace("\n", "").replace("\r", "")

        if state == 'OK':
            self.connection_established = True
            logging.info("Spojeni navazano.")
        elif state == 'ERR':
            error_note = register_response[4]
            error_note = error_note.replace("\n", "").replace("\r", "")
            if error_note == 'NONEXISTING_OR':
                logging.error("Neexistujicí oblast řízení...")
            elif error_note == 'ALREADY_REGISTERED':
                logging.error("OŘ již byla registrovná.")
            elif error_note == 'INTERNAL_ERROR':
                logging.error("Vnitřní chyba serveru, více info na serveru")

    def connect(self, ip, port):

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))

            return client_socket

        except socket.error:
            # raise TCPCommunicationEstablishedError("Server neni zapnuty!")
            logging.warning("Nepodarilo se navazat komunikaci se serverem Error")

        except socket.timeout:
            logging.warning("TCP Timeout")
            # raise TCPTimeoutError("TCP Timeout")

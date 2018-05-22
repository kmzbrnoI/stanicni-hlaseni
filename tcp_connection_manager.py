#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import socket
import threading
import time
import os
from datetime import datetime 
from collections import deque

import message_parser
import process_report
import report_manager
import system_functions


class TCPCommunicationEstablishedError(OSError):
    pass


class TCPTimeoutError(OSError):
    pass


class OutdatedVersionError(Exception):
    pass


class TCPConnectionManager:
    def __init__(self):
        self.rm = report_manager.ReportManager()
        self.device_info = system_functions.DeviceInfo()
        self.server_ip = ""
        self.server_port = ""
        self.connection_established = False

    def listen(self, socket):
        message_part = ""
        message_queue = deque()

        while True:
            try:
                message = socket.recv(2048)

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

                decoded_message = message.decode('UTF-8')
                decoded_message = decoded_message.replace("\r", "") #rovnou vyhodit \r 
                message_queue += decoded_message.splitlines(True)

                while message_queue:
                    
                    if message_queue[-1].endswith('\n'):  # vše ok
                        message_to_process = message_queue.popleft()
                        
                        message_to_process = message_to_process.replace("\n", "")

                        if "-;HELLO" in message_to_process:
                            self.process_hello_response(socket, message_to_process)
                        elif "REGISTER-RESPONSE;" in message_to_process:
                            self.process_register_response(socket, message_to_process)
                        elif "SYNC" in message_to_process:
                            self.sync(socket, message_to_process)
                        elif "CHANGE-SET" in message_to_process:
                            self.change_set(socket, message_to_process)
                        elif "SETS-LIST" in message_to_process:
                            self.sets_list(socket, message_to_process)
                        elif "NESAHAT" in message_to_process:
                            threading.Thread(target=process_report.nesahat()).start()
                        elif "POSUN" in message_to_process:
                            threading.Thread(target=process_report.posun()).start()
                        elif (('SH;PRIJEDE;' in message_to_process) or ("SH;ODJEDE;" in message_to_process) or (
                                "SH;PROJEDE;" in message_to_process)) and self.connection_established:
                            logging.debug("Zpracovava se: {0}".format(message_to_process))
                            threading.Thread(target=process_report.process_message(message_to_process)).start()
                    else:
                        # vyhodím poslední prvek z bufferu a připojím na začátek nové zprávy
                        message_part = message_queue.popleft()
                        break

            except OSError as e:
                logging.warning("Connection error: {0}".format(e))
                break
            
            except Exception as e:
                logging.warning("Connection error: {0}".format(e))
                break

    def send_message(self, socket, message):
        try:
            socket.send(message.encode('UTF-8'))
            
        except TCPCommunicationEstablishedError:
            logging.error("Nepodarilo se odeslat zpravu na serveru...")
           
        except socket.timeout:
            logging.warning("TCP Timeout...")
           
    def process_hello_response(self, socket, message):

        hello_message = message_parser.parse(message, ";")
        version = hello_message[-1]
        version = version.replace("\n", "")
        version = version.replace("\r", "")

        version = float(version)

        logging.debug("Verze hello: {0}".format(version))

        if version >= 1:
            register_message = self.device_info.area + ";SH;REGISTER;"+ self.rm.sound_set +";1.0\n"
            self.send_message(socket, register_message)

        else:
            raise OutdatedVersionError("Je potreba aktualizovat verzi..")

    def process_register_response(self, socket, message):
        register_response = message_parser.parse(message, ";")

        state = register_response[3]

        state = state.replace("\n", "").replace("\r", "")

        if state == 'OK':
            self.connection_established = True
            logging.info("Spojení navázano")
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
            client_socket.settimeout(50)
            client_socket.connect((ip, port))

            return client_socket

        except OSError as e:
            logging.warning("Connection error: {0}".format(e))
                
        except Exception as e:
            logging.warning("Connection error: {0}".format(e))


    def sync(self, socket, message):

        info_message = self.device_info.area + ";SH;SYNC;STARTED;\n"
        self.send_message(socket, info_message)

        sound_set = self.rm.sound_set
        #aktualizace zvukové sady, podle config.ini
        return_code, output, error = system_functions.download_sound_files_samba("server-tt", "shZvuky", sound_set)

        version = "1.0"

        return_code = str(return_code)

        if return_code == '0':
            logging.info("Aktualizace zvukové sady proběhla úspěšně.")
            info_message = self.device_info.area + ";SH;SYNC;DONE;" + sound_set + ";" + version + "\n"
        else:
            logging.error("Při aktualizace zvukové sady nastala chyba.")
            info_message = self.device_info.area + ";SH;SYNC;ERR;" + version + ";" + str(error) + "\n"

        self.send_message(socket, info_message)

    def sets_list(self, socket, message):

        sound_sets = system_functions.list_samba("server-tt", "shZvuky")

        sounds_set_string = ""
        sounds_set_string = ",".join(sound_sets )
            
        info_message = self.device_info.area + ";SH;SETS-LIST;{" + sounds_set_string + "};\n"
        self.send_message(socket, info_message)

    def change_set(self, socket, message):
        parsed_message = message_parser.parse(message, ";")
        sound_set = parsed_message[3]

        available = os.path.isdir('./' + sound_set)

        if available :
            self.rm.sound_set = sound_set
            info_message = self.device_info.area + ";SH;CHANGE-SET;OK;\n"
        else :
            info_message = self.device_info.area + ";SH;CHANGE-SET;ERR;SET_NOT_AVAILABLE\n"

        self.send_message(socket, info_message)


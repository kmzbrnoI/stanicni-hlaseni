#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import socket
import time
from collections import deque
from os import path

import message_parser
import process_report
import report_manager
import system_functions


class TCPCommunicationEstablishedError(Exception):
    pass


class TCPTimeoutError(OSError):
    pass


class OutdatedVersionError(Exception):
    pass


class TCPConnectionManager:
    def __init__(self, ip, port, device_info):
        self.device_info = device_info
        self.rm = report_manager.ReportManager(
            self.device_info.soundset,
            self.device_info.soundset_path,
            self.device_info.area
        )

        self.connect(ip, port)
        self.send('-;HELLO;1.0')
        self.listen()

    def listen(self):
        previous = ''

        try:
            while True:
                recv = previous + \
                       self.socket.recv(2048).decode('utf-8').replace('\r', '')

                if '\n' not in recv:
                    continue

                q = deque(recv.splitlines(keepends=True))
                self.gong_played = False

                while q:
                    item = q.popleft()
                    logging.debug("> {0}".format(item.strip()))

                    if item.endswith('\n'):
                        try:
                            self.process_message(item.strip())
                        except Exception as e:
                            logging.warning("Mesasge processing error: "
                                            "{0}!".format(str(e)))
                    else:
                        previous = item

                if self.gong_played:
                    self.rm.create_report([os.path.join("gong", "gong_end.ogg")])

        except Exception as e:
            logging.error("Connection error: {0}".format(e))

    def send(self, message):
        try:
            if message is not None:
                logging.debug("< {0}".format(message))
                self.socket.send((message + '\n').encode('UTF-8'))
            else:
                raise TCPCommunicationEstablishedError  # TODO: really?

        except TCPCommunicationEstablishedError:
            logging.error("TCPCommunicationEstablishedError!")

        except (TypeError, AttributeError):
            logging.critical("Unable to send message!")
            time.sleep(60)

        except Exception as e:
            logging.warning("Connection exception: {0}".format(e))

    def process_message(self, message):
        parsed = message_parser.parse(message, [';'])
        if len(parsed) < 2:
            return

        parsed[1] = parsed[1].upper()

        if parsed[1] == 'HELLO':
            self.process_hello(parsed)
            self.send(self.device_info.area + ";SH;REGISTER;" +
                      self.rm.sound_set + ";1.0")

        if parsed[1] != 'SH':
            return

        parsed[2] = parsed[2].upper()

        if parsed[2] == "REGISTER-RESPONSE":
            self.process_register_response(parsed)
        elif parsed[2] == "SYNC":
            self.sync(parsed)
        elif parsed[2] == "CHANGE-SET":
            self.change_set(parsed)
        elif parsed[2] == "SETS-LIST":
            self.send_sets_list()
        elif parsed[2] == "SPEC":
            if parsed[3] == "NESAHAT":
                process_report.nesahat(self.rm)
            elif parsed[3] == "POSUN":
                process_report.posun(self.rm)
        elif parsed[2] == "PRIJEDE" or parsed[2] == "ODJEDE" or parsed[2] == "PROJEDE":
            if not self.gong_played:
                self.rm.create_report([
                    os.path.join("gong", "gong_start.ogg"),
                    os.path.join("salutation", "vazeni_cestujici.ogg")
                ])
                self.gong_played = True

            process_report.process_message(message, self.rm)

    def process_hello(self, parsed):
        version = float(parsed[2])
        logging.info("Server version: {0}.".format(version))

        if version < 1:
            raise OutdatedVersionError("Outdated version of server protocol: "
                                       "{0}!".format(version))

    def process_register_response(self, parsed):
        state = parsed[3].upper()

        if state == 'OK':
            logging.info("Successfully registered to "
                         "{0}.".format(self.device_info.area))

        elif state == 'ERR':
            error_note = parsed[4].upper()
            logging.error("Register error: {0}".format(error_note))
            # TODO: what to do here?
        else:
            logging.error("Invalid state: {0}!".format(state))
            # TODO: what to do here?

    def connect(self, ip, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(50)
            self.socket.connect((ip, port))
        except Exception as e:
            logging.warning("Connect exception: {0}".format(e))
            self.socket = None

    def sync(self, parsed):  # TODO: check for errors and refactoring
        # Vytvorim si docasny report_manager
        tmp_rm = report_manager.ReportManager(self.device_info.soundset, self.device_info.area)
        logging.debug("Default set: {0}".format(self.device_info.soundset))

        # Vylistuji sambu a ziskam dostupne sady

        sound_sets = system_functions.list_samba(self.device_info.smb_server, self.device_info.smb_home_folder)
        logging.debug("Available sets: {0}".format(sound_sets))

        updated = []

        # Oznamim serveru aktualizaci zvukovych sad

        info_message = self.device_info.area + ";SH;SYNC;STARTED;"
        self.send(info_message)

        print(tmp_rm.sound_set)
        while True:
            if (tmp_rm.sound_set in sound_sets) and (tmp_rm.sound_set not in updated):

                logging.debug("Downloading {0}...".format(tmp_rm.sound_set))

                # aktualizace zvukové sady, podle config.ini
                return_code, output, error = system_functions.download_sound_files_samba(
                    self.device_info.smb_server,
                    self.device_info.smb_home_folder,
                    str.strip(tmp_rm.sound_set))

                if str(return_code) == '0':
                    logging.debug("{0} downloaded succesfully.".format(tmp_rm.sound_set))
                    updated.append(tmp_rm.sound_set)

                    if tmp_rm.parent_sound_set in updated:
                        logging.debug("Parent sound set for {0} is downloaded. ({1})".format(tmp_rm.sound_set,
                                                                                             tmp_rm.parent_sound_set))
                        break
                    else:
                        tmp_rm = report_manager.ReportManager(tmp_rm.parent_sound_set, self.device_info.area)
                        tmp_rm.load_sound_config()
                        logging.debug("{0} required.".format(tmp_rm.sound_set))

                else:
                    # nastala chyba pri aktualizaci zvukove sady
                    logging.debug("Non-return code when downloading {0}".format(tmp_rm.sound_set))
                    break

            else:
                logging.debug("Downloading finished.")
                break

        version = "1.0"

        return_code = str(return_code)

        if return_code == '0':
            logging.info("Soundset update done..")
            info_message = self.device_info.area + ";SH;SYNC;DONE;" + tmp_rm.sound_set + ";" + version + "\n"
        elif return_code == '99':
            logging.info("Soundset update error: {0} not found on server!".format(
                tmp_rm.sound_set))
            info_message = self.device_info.area + ";SH;SYNC;ERR;" + version + ";" + str(error)
        else:
            logging.error("Soundset update error!")
            info_message = self.device_info.area + ";SH;SYNC;ERR;" + version + ";" + str(error)

        self.send(info_message)

    def send_sets_list(self):
        sound_sets = system_functions.list_samba(self.device_info.smb_server, self.device_info.smb_home_folder)

        sounds_set_string = ",".join(sound_sets)

        info_message = self.device_info.area + ";SH;SETS-LIST;{" + sounds_set_string + "};"
        self.send(info_message)

    def change_set(self, parsed):
        sound_set = parsed[3]

        if path.isdir('./' + sound_set):  # TODO: refactor!
            self.rm.sound_set = sound_set
            self.rm.load_sound_config()
            info_message = self.device_info.area + ";SH;CHANGE-SET;OK;"
        else:
            info_message = self.device_info.area + ";SH;CHANGE-SET;ERR;SET_NOT_AVAILABLE"

        self.send(info_message)

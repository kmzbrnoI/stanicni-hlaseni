"""
This file defined TCPConnectionManager class which handles TCP communication
with hJOPserver. It creates instance of ReportManager in __init___ and calls
its methods based on received data.
"""

import logging
import os
import socket
import time
from collections import deque
from os import path
import traceback
import select

import message_parser
import report_manager
import soundset_manager
from soundset import SoundSet
import device_info


class TCPCommunicationEstablishedError(Exception):
    pass


class TCPTimeoutError(OSError):
    pass


class OutdatedVersionError(Exception):
    pass


class SambaNotDefined(Exception):
    pass

class DisconnectedError(Exception):
    pass


class TCPConnectionManager:
    def __init__(self, ip, port, device_info):
        self.device_info = device_info
        self.rm = report_manager.ReportManager(self.device_info)
        self.gong_played = False

        self._connect(ip, port)
        self._send('-;HELLO;1.0')
        self._listen()

    def _listen(self):
        previous = ''

        try:
            while self.socket:
                data = self.socket.recv(2048)
                if not data:
                    raise DisconnectedError("Disconnected from server!")

                recv = previous + data.decode('utf-8').replace('\r', '')
                previous = ''

                if '\n' not in recv:
                    if self.gong_played:
                        self.rm.play_raw_report(
                            [os.path.join("gong", "gong_end")]
                        )
                    self.gong_played = False
                    previous = recv
                    continue

                q = deque(recv.splitlines(keepends=True))

                while q:
                    item = q.popleft()
                    logging.debug("> {0}".format(item.strip()))

                    if item.endswith('\n'):
                        try:
                            self._process_message(item.strip())
                        except Exception as e:
                            logging.warning("Message processing error: "
                                            "{0}!".format(str(e)))
                            traceback.print_exc()
                    else:
                        previous = item

                # Play gong if no data at input
                readable, _, _ = select.select([self.socket], [], [], 0)
                if not readable and self.gong_played:
                    self.rm.play_raw_report([os.path.join("gong", "gong_end")])
                    self.gong_played = False

        except Exception as e:
            logging.error("Connection error: {0}".format(e))

    def _send(self, message):
        try:
            if self.socket:
                logging.debug("< {0}".format(message))
                self.socket.send((message + '\n').encode('UTF-8'))

        except Exception as e:
            logging.error("Connection exception: {0}".format(e))

    def _process_message(self, message):
        parsed = message_parser.parse(message, [';'])
        if len(parsed) < 2:
            return

        parsed[1] = parsed[1].upper()

        if parsed[1] == 'HELLO':
            self._process_hello(parsed)
            self._send(self.device_info.area + ";SH;REGISTER;" +
                      self.rm.soundset.name + ";1.0")

        if parsed[1] != 'SH' or parsed[0] != self.device_info.area:
            return

        parsed[2] = parsed[2].upper()

        if parsed[2] == "REGISTER-RESPONSE":
            self._process_register_response(parsed)
        elif parsed[2] == "SYNC":
            self._process_sync(parsed)
        elif parsed[2] == "CHANGE-SET":
            self._process_change_set(parsed)
        elif parsed[2] == "SETS-LIST":
            self._process_sets_list()
        elif parsed[2] == "PRIJEDE" or parsed[2] == "ODJEDE" \
             or parsed[2] == "PROJEDE" or parsed[2] == "SPEC":
            if not self.gong_played and self.rm.soundset.play_gong:
                self.rm.play_raw_report([
                    os.path.join("gong", "gong_start"),
                ])
                self.gong_played = True

            if parsed[2] == "SPEC":
                self.rm.process_spec_message(parsed[3].upper())
            else:
                self.rm.process_trainset_message(parsed)

    def _process_hello(self, parsed):
        version = float(parsed[2])
        logging.info("Server version: {0}.".format(version))

        if version < 1:
            raise OutdatedVersionError("Outdated version of server protocol: "
                                       "{0}!".format(version))

    def _process_register_response(self, parsed):
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

    def _connect(self, ip, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(50)
            self.socket.connect((ip, port))
        except Exception as e:
            logging.warning("Connect exception: {0}".format(e))
            self.socket = None

    def _process_sets_list(self):
        sound_sets = soundset_manager.get_local_sets_list(
            self.device_info.soundset_path
        )

        if self.device_info.smb_server and self.device_info.smb_home_folder:
            sound_sets += soundset_manager.get_samba_sets_list(
                self.device_info.smb_server,
                self.device_info.smb_home_folder,
                self.device_info.soundset_path,
            )

        self._send(
            self.device_info.area + ';SH;SETS-LIST;{' +
            ','.join(set(sound_sets)) + '}'
        )

    def _process_sync(self, parsed):
        self._send(self.device_info.area + ";SH;SYNC;STARTED;")

        if not self.device_info.smb_server or not self.device_info.smb_home_folder:
            self._send(self.device_info.area + ";SH;SYNC;ERR;;Samba není nakonfigurována!")
            return

        ro = False
        try:
            ro = soundset_manager.is_ro(self.device_info.soundset_path)
            if ro:
                soundset_manager.remount_rw(self.device_info.soundset_path)

            soundset_manager.sync(
                server=self.device_info.smb_server,
                home_folder=self.device_info.smb_home_folder,
                soundset=self.device_info.soundset,
                soundset_path=self.device_info.soundset_path,
            )
            self.rm.soundset = SoundSet(
                self.device_info.soundset_path, self.device_info.soundset
            )

            self._send(self.device_info.area + ";SH;SYNC;DONE;" +
                       self.device_info.soundset + ";")
        except Exception as e:
            # DEBUG:
            logging.warning("Download error: "
                            "{0}!".format(str(e)))
            traceback.print_exc()

            self._send(self.device_info.area + ";SH;SYNC;ERR;" +
                       ";" + str(e))
        finally:
            if ro:
                soundset_manager.remount_ro(self.device_info.soundset_path)

    def _process_change_set(self, parsed):
        ro = False
        try:
            ro = soundset_manager.is_ro(self.device_info.soundset_path)
            if ro:
                soundset_manager.remount_rw(self.device_info.soundset_path)

            soundset_manager.change_set(
                soundset=parsed[3],
                soundset_path=self.device_info.soundset_path,
                server=self.device_info.smb_server,
                home_folder=self.device_info.smb_home_folder,
            )
            self.rm.soundset = SoundSet(
                self.device_info.soundset_path, parsed[3]
            )
            self.device_info.soundset = parsed[3]
            self.device_info.store(device_info.GLOBAL_CONFIG_FILENAME)

            self._send(self.device_info.area + ";SH;CHANGE-SET;OK;")
        except Exception as e:
            # DEBUG:
            logging.warning("Download error: "
                            "{0}!".format(str(e)))
            traceback.print_exc()

            self._send(self.device_info.area + ";SH;CHANGE-SET;ERR;" + str(e))
        finally:
            if ro:
                soundset_manager.remount_ro(self.device_info.soundset_path)

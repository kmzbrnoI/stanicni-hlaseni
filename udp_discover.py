#!/usr/bin/env python3

import logging
import socket
import time
import sys

import system_functions


DISCOVER_PORT = 5880
NO_TRY = 3


class ServerNotFoundError(Exception):
    pass


class InvalidProtocolError(Exception):
    pass


class InvalidVersionError(Exception):
    pass


class ServerInfo:
    """This class holds info about server discovered via UDP discover."""

    def __init__(self, udp_str):
        splitted = udp_str.split(';')

        if splitted[0] != 'hJOP':
            raise InvalidProtocolError()

        if splitted[1].split('.')[0] != '1':
            raise InvalidVersionError()

        self.type = splitted[2]
        self.name = splitted[3]
        self.ip = splitted[4]
        self.port = int(splitted[5]) if splitted[5] else 0
        self.status = splitted[6]
        self.on = (self.status == 'on')
        self.description = splitted[7]

    def __str__(self):
        return (self.name + ' ' + self.description + ' ' + self.ip + ' ' +
                str(self.port))

    __repr__ = __str__


def find_server(name: str) -> ServerInfo:
    """
    Finds server with name 'name', returns instance of ServerInfo or
    ServerNotFoundError when server was not found.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', DISCOVER_PORT))
    s.settimeout(5)

    for i in range(NO_TRY):
        s.sendto(
            ("hJOP;1.0;sh;;" + system_functions.get_device_ip() + ";;;\n")
            .encode('utf-8'),
            ('<broadcast>', DISCOVER_PORT)
        )

        try:
            while True:
                message, (ip, port) = s.recvfrom(4096)
                messages = message.decode('utf-8').strip().split('\n')
                for m in messages:
                    logging.debug('> ' + m)

                    try:
                        server = ServerInfo(m)
                    except Exception as e:
                        logging.error(str(e))
                        continue

                    if server.type == 'server':
                        if server.description == name and server.on:
                            return server

        except socket.timeout:
            raise ServerNotFoundError("Server not found!")

    raise ServerNotFoundError("Server not found!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: ./udp_discover.py server_name\n")
        sys.exit(1)

    print("Server found:", find_server(sys.argv[1]))

#!/usr/bin/env python3

import logging
import os
import time

import system_functions
import tcp_connection_manager
import udp_discover


def get_logging_level(verbosity):
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }.get(verbosity, logging.DEBUG)


def main():
    device_info = system_functions.DeviceInfo()

    logging.basicConfig(
        level=get_logging_level(device_info.verbosity),
        filename=device_info.path if device_info.path else None
    )

    client = tcp_connection_manager.TCPConnectionManager()

    while True:
        try:
            server = udp_discover.find_server(device_info.server_name)
            logging.debug("Server found: {0}:{1}".format(server.ip, server_port))

            for _ in range(5):
                logging.debug("TCP pokus {0}".format((_ + 1)))
                client_socket = client.connect(server.ip, int(server_port))
                hello_message = "-;HELLO;1.0\n"
                client.send_message(client_socket, hello_message)
                client.listen(client_socket)

        except tcp_connection_manager.TCPCommunicationEstablishedError:
            logging.error("TCPCommunicationEstablishedError!")

        except tcp_connection_manager.TCPTimeoutError:
            logging.warning("TCP Timeout!")

        except udp_discover.ServerNotFoundError:
            time.sleep(10)
            logging.error("Server not found!")

        except tcp_connection_manager.OutdatedVersionError:
            logging.critical("Outdated version of server!")
            break


if __name__ == "__main__":
    main()

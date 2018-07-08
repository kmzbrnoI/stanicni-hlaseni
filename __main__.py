#!/usr/bin/env python3

"""
This is a main service executable file. Use it to start Station Announcement.
"""

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

    while True:
        try:
            server = udp_discover.find_server(device_info.server_name)
            logging.info("Server found: {0}:{1}.".format(server.ip, server.port))

            client = tcp_connection_manager.TCPConnectionManager(server.ip, server.port, device_info)

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

        time.sleep(1)


if __name__ == "__main__":
    main()

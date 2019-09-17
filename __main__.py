#!/usr/bin/env python3

"""
This is a main service executable file. Use it to start Station Announcement.
"""

import logging
import time

from device_info import DeviceInfo
import tcp_connection_manager
import udp_discover


def get_logging_level(verbosity: str):
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }.get(verbosity, logging.DEBUG)


def main():
    device_info = DeviceInfo()

    logging.basicConfig(
        level=get_logging_level(device_info.verbosity),
        filename=device_info.path if device_info.path else None
    )

    while True:
        try:
            server = udp_discover.find_server(device_info.server_name)
            logging.info(
                'Server found: {0}:{1}.'.format(server.ip, server.port)
            )

            tcp_connection_manager.TCPConnectionManager(
                server.ip, server.port, device_info
            )

        except tcp_connection_manager.TCPCommunicationEstablishedError:
            logging.error('TCPCommunicationEstablishedError!')

        except tcp_connection_manager.TCPTimeoutError:
            logging.warning('TCP Timeout!')

        except udp_discover.ServerNotFoundError:
            time.sleep(10)
            logging.error('Server not found!')

        except tcp_connection_manager.OutdatedVersionError:
            logging.critical('Outdated version of server!')
            break

        except tcp_connection_manager.DisconnectedError:
            logging.error('Disconnected from server!')

        except IOError as e:
            if e.errno == 101:  # Network in unreachable
                logging.error('Network is unreachable!')
                time.sleep(10)
            else:
                raise

        time.sleep(1)


if __name__ == '__main__':
    main()

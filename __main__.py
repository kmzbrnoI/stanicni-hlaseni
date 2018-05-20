#!/usr/bin/env python3

import logging
import os
import socket
import time

import tcp_connection_manager
import system_functions
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

    verbosity = get_logging_level(device_info.verbosity)
    path = os.path.join(device_info.path, 'sh.log')
    logging.basicConfig(filename=path,level=verbosity)
    
    
    while True:
        if system_functions.setup_wifi(device_info.ssid) :
            break
     
    server_ip = ''
    client = tcp_connection_manager.TCPConnectionManager()
    
    while True:

        try:

            while not server_ip:
                server_ip, server_port = udp_discover.get_ip(device_info.server_name)

            logging.debug("Server nalezen: {0}:{1}".format(server_ip, server_port))

            for _ in range(5):
                logging.debug("TCP pokus {0}".format((_ + 1)))

                client_socket = client.connect(server_ip, int(server_port))

                hello_message = "-;HELLO;1.0\n"

                client.send_message(client_socket, hello_message)

                client.listen(client_socket)

            server_ip = ''

        except tcp_connection_manager.TCPCommunicationEstablishedError:
            logging.error("Nepovedlo se navazani komunikace pres TCP")

        except tcp_connection_manager.TCPTimeoutError:
            logging.warning("TCP Timeout.")

        except udp_discover.ServerNotFoundError:
            time.sleep(30)
            logging.error("Server nenalezen.")

        except udp_discover.UDPTimeoutError:
            logging.error("UDP Timeout.")
            time.sleep(5)

        except tcp_connection_manager.OutdatedVersionError:
            logging.critical("Zastarala verze na serveru.")
            break


if __name__ == "__main__":
    main()

import logging
import socket
import time

import network_services_client
import system_functions
import udp_discover


def main():
    logging.basicConfig(level=logging.DEBUG)
    server_ip = ''
    client = network_services_client.NetworkServicesClient()
    device_info = system_functions.DeviceInfo()

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

        except network_services_client.TCPCommunicationEstablishedError:
            logging.error("Nepovedlo se navazani komunikace pres TCP")

        except network_services_client.TCPTimeoutError:
            logging.warning("TCP Timeout.")

        except udp_discover.ServerNotFoundError:
            time.sleep(30)
            logging.error("Server nenalezen.")

        except udp_discover.UDPTimeoutError:
            logging.error("UDP Timeout.")
            time.sleep(5)

        except network_services_client.OutdatedVersionError:
            logging.critical("Zastaralá verze na serveru.")


if __name__ == "__main__":
    main()

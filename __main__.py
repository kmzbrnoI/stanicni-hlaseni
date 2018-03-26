import socket

import network_services_client
import system_functions
import udp_discover


class OutdatedVersionError(Exception):
    pass


def main():
    try:
        device_info = system_functions.DeviceInfo()
        server_ip, server_port = udp_discover.get_ip(device_info.server_name)
        client = network_services_client.NetworkServicesClient()

        for _ in range(5):
            print("TCP pokus ", _ + 1)
            client_socket, version = client.connect(server_ip, int(server_port))

            if version >= 1:
                registered_socket = client.register_device(client_socket)
                if registered_socket:
                    client.listen(registered_socket)

            else:
                raise OutdatedVersionError("Je potreba aktualizovat verzi..")

    except network_services_client.TCPCommunicationEstablishedError:
        print("Nepovedlo se navazani komunikace pres TCP")

    except network_services_client.TCPTimeoutError:
        print("TCP Timeout.")

    except udp_discover.ServerNotFoundError:
        print("Server nenalezen.")

    except udp_discover.UDPTimeoutError:
        print("UDP Timeout.")

    except OutdatedVersionError:
        print("Zastaralá verze na serveru.")


if __name__ == "__main__":
    main()

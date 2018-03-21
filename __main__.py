import network_services_client
import udp_discover
import system_functions


def main():
    try:
        device_info = system_functions.DeviceInfo()
        server_ip, server_port = udp_discover.get_ip(device_info.server_name)
        client = network_services_client.NetworkServicesClient()
        client.tcp_listener(5896)

    except udp_discover.ServerNotFoundError:
        print("Server nenalezen.")

    except udp_discover.UDPTimeoutError:
        print("UDP Timeout.")


if __name__ == "__main__":
    main()

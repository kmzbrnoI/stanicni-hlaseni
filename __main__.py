import network_services_client


def main():
    client = network_services_client.NetworkServicesClient()
    if client.udp_broadcast_listener(5880):
        client.tcp_listener(5896)
    else:
        print("Nepovedlo se navazat UDP spojeni se serverem...")


if __name__ == "__main__":
    main()

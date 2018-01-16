#!/usr/bin/python3

import socket
import time
import threading
import asyncio
import report_manager

connection_attempts = 0


def get_connection_attempts():
    global connection_attempts
    return connection_attempts


def add_connection_attempts():
    global connection_attempts
    connection_attempts += 1


def tcp_listener(port):
    communication_accomplished = False
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        while (communication_accomplished == False) and (get_connection_attempts() < 5):
            add_connection_attempts()

            try:
                clientsocket.connect((host, port))
                communication_accomplished = True
            except socket.error:
                print("Server neni zapnuty!")
                print("Pocet pokusu: ", get_connection_attempts())
                time.sleep(1)
                if get_connection_attempts() >= 5:
                    print("Ukoncuji spojeni")
                    break;
                tcp_listener(port)

        if (communication_accomplished):
            print("Zarizeni je pripraveno k prijmu dat...")
            message = ""
            while True:
                try:
                    message = clientsocket.recv(1024)
                    decoded_message = message.decode('UTF-8')
                    if decoded_message == "ukoncit":
                        break
                    report_list = decoded_message.split(" ")
                    report_manager.create_report(report_list, 1)
                    print(message.decode('UTF-8'))
                except socket.error:
                    print("Nastala chyba pri prijmu dat...")

            # communication_accomplished = False
            print("Server ukoncil spojeni...")
            clientsocket.close()
            print("Ukoncuji tcp_listener...")

        else:
            print("Spojeni se nepovedlo navazat, zarizeni neni pripraveno k prijmu dat...")

    except socket.timeout:
        print("Nepovedlo se navazat spojeni!")
        communication_accomplished = False


tcp_listener(9999)

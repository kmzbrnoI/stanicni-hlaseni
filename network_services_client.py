#!/usr/bin/python3

import socket
import threading, time

import message_parser
import report_manager
import system_functions
import process_message


class TCPCommunicationEstablishedError(socket.error):
    pass


class TCPTimeoutError(socket.timeout):
    pass


class NetworkServicesClient():
    def __init__(self):
        self.rm = report_manager.ReportManager()
        self.device_info = system_functions.DeviceInfo()
        self.server_ip = ""
        self.server_port = ""

    def listen(self, socket):
        message_part = ""
        while True:
            try:
                message = socket.recv(1024)
                
                if message_part :
                    #předchozí zpráva došla po částech
                    message = message_part.encode('UTF-8') + message
                    message_part = ""
                          
                while True :
                    #pokud zprava neobsahuje \n přijímám dál...
                    if '\n' in message.decode('UTF-8') :
                        break
                    else :
                         message += socket.recv(1024)

                decoded_message = message.decode('UTF-8')

                buffer = decoded_message.splitlines(True)

                #print("Buffer :", buffer)

                if buffer :

                    if buffer[-1].endswith('\n'): #vše ok

                        message_to_process = buffer.pop(0) 

                        if message_to_process == "ukoncit":
                            break

                        if "-;PING" in message_to_process:
                            continue

                        if 'SH' in message_to_process:
                            threading.Thread(target=process_message.process_message([message_to_process])).start()
                            
                    else :
                        #poslední prvek připojím na začátek nové zprávy
                        message_part = buffer.pop()
                
            except socket.error:
                print("Nastala chyba pri prijmu dat...")

            except socket.timeout:
                print("TCP Timeout")

    def connect(self, ip, port):

        try:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            clientsocket.settimeout(20)
            clientsocket.connect((ip, port))
            clientsocket.send("-;HELLO;1.0\n".encode('UTF-8'))

            message = self.receive_special_message(clientsocket, "-;HELLO")
            
            if 'hello' in message.lower() : #muze se stat, ze zrovna prijde ping
                
                hello_message = message_parser.parse(message, ";")

                version = hello_message[-1]

                version = version.replace("\n", "")
                version = version.replace("\r", "")

                version = float(version)

                print("Verze hello: ", version)

                return (clientsocket, version)


        except socket.error:
            # raise TCPCommunicationEstablishedError("Server neni zapnuty!")
            print("Nepodarilo se navazat komunikaci se serverem Error")

        except socket.timeout:
            print("TCP Timeout")
            # raise TCPTimeoutError("TCP Timeout")

    def register_device(self, socket):
        register_message = self.device_info.area + ";SH;REGISTER\n";
        socket.send(register_message.encode('UTF-8'))  # musím na server odeslat registrační zprávu

        message = self.receive_special_message(socket, "-;MOD-CAS")

        if message:  # tady potom přidat try, zda OŘ existuje
            return socket


    def receive_special_message(self, socket, reply):
        #metoda slouží pro příjem potvrzovací odpovědi na speciální zprávu napr. HELLO
        message_part = ""
        
        message = socket.recv(512)
        
        if message_part :
            #předchozí zpráva došla po částech
            message = message_part.encode('UTF-8') + message
            message_part = ""
                  
        while True :
            #pokud zprava neobsahuje \n přijímám dál...
            if '\n' in message.decode('UTF-8') :
                break
            else :
                 message += socket.recv(512)

        decoded_message = message.decode('UTF-8')

        buffer = decoded_message.splitlines(True)

        if buffer :

            if buffer[-1].endswith('\n'): #vše ok

                for item in buffer :
                    #v bufferu mohou být klidně dvě zprávy
                    if reply in item :
                        return item
                    
            else :
                #poslední prvek připojím na začátek nové zprávy
                message_part = buffer.pop()

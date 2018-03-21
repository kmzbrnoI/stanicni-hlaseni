#!/usr/bin/python3

import os
import subprocess
import socket
from configparser import ConfigParser


def play_sound(file_name):
    os.system('aplay ' + str(file_name))


def download_sound_files_github():
    clone = "git clone https://github.com/kmzbrnoI/shZvuky"
    os.system(clone)


def download_sound_files_samba(server_ip, home_folder, sound_set):
    subprocess.call(["./download_sound_set.sh", server_ip, home_folder, sound_set]);


def get_device_ip():

    return socket.gethostbyname(socket.gethostname())

def setup_wifi():
    subprocess.call(["./wifi.sh"])
    
    
class DeviceInfo:

    def __init__(self):
      self.ssid = ''
      self.password = ''
      self.server_name = ''
      self.area = ''
      self.read_device_config()


    def read_device_config(self):
        # funkce pro načtení konfiguračního souboru
        parser = ConfigParser()
        parser.read('global_config.ini')

        wifi = parser.sections()[0]
        self.ssid = (parser[wifi]['ssid'])
        self.password = (parser[wifi]['password'])
        server = parser.sections()[1]
        self.server_name = (parser[server]['name'])
        area = parser.sections()[2]
        self.area = (parser[area]['name'])


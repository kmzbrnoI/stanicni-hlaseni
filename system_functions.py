#!/usr/bin/python3

import os
import subprocess
from configparser import ConfigParser


def play_sound(file_name):
    os.system('aplay ' + str(file_name))


def download_sound_files_github():
    clone = "git clone https://github.com/kmzbrnoI/shZvuky"
    os.system(clone)


def download_sound_files_samba(server_ip, home_folder, sound_set):
    subprocess.call(["./download_sound_set.sh", server_ip, home_folder, sound_set]);


def get_device_ip():
    return str(subprocess.check_output("hostname -I", shell=True))


def setup_wifi():
    subprocess.call(["./wifi.sh"])
    
    
class DeviceInfo:

    def __init__(self):
      self.ssid = ''
      self.password = ''
      self.server_name = ''
      self.read_device_config()


    def read_device_config(self):
        # funkce pro načtení konfiguračního souboru
        parser = ConfigParser()
        parser.read('device_config.ini')

        wifi = parser.sections()[0]
        self.ssid = (parser[wifi]['ssid'])
        self.password = (parser[wifi]['password'])
        server = parser.sections()[1]
        self.server_name = (parser[server]['name'])

        #print("SSID: {0}\nPassword: {1}".format(self.ssid, self.password))


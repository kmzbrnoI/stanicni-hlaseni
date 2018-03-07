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


def read_device_config():
    # funkce pro načtení konfiguračního souboru
    parser = ConfigParser()
    parser.read('device_config.ini')

    sound_set = parser.sections()[0]
    ssid = (parser[sound_set]['ssid'])
    password = (parser[sound_set]['password'])

    print("SSID: {0}\nPassword: {1}".format(ssid, password))


def setup_wifi():
    subprocess.call(["./wifi.sh"])

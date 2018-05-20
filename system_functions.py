import logging
import os
import socket
import subprocess
import time
from configparser import ConfigParser
from subprocess import Popen, PIPE, DEVNULL


def play_sound(file_name):
    os.system('aplay ' + str(file_name))


def download_sound_files_github():
    clone = "git clone https://github.com/kmzbrnoI/shZvuky"
    os.system(clone)


def list_samba(server_ip, home_folder):
    sound_sets = []
    process = Popen(['./list_samba.sh', server_ip, home_folder], stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()
    sound_sets = output.decode('utf-8').splitlines()[2:] #. .. Veronika Zbynek
    
    return sound_sets
    

def download_sound_files_samba(server_ip, home_folder, sound_set):
    try:
        logging.info("Aktualizace zvukove sady: {0}".format(sound_set))
        process = Popen(['./download_sound_set.sh', server_ip, home_folder, sound_set], stdout=PIPE, stderr=PIPE)

        # Pro jistotu nastavuji timeout na 60s.
        output, error = process.communicate(timeout=60)
        
        return (process.returncode, output, error)

    except subprocess.TimeoutExpired as e:
        # odchytávám jenom v případě timeout, všechny ostatní chyby jsou uloženy v process
        
        # vracet vyjimku
        return (1, "timeout", "timeout")


def get_device_ip():
    return socket.gethostbyname(socket.gethostname())


def setup_wifi(wifi_ssid):

    proc = Popen(["iwgetid"], stdout=PIPE, stderr=PIPE)
    connected, err = proc.communicate()
    exitcode = proc.returncode
    
    if not wifi_ssid in str(connected) :
        print("Zapinam  WIFI")
        proc = Popen(["./wifi.sh"], stderr=DEVNULL, stdout=DEVNULL)
        connected, err = proc.communicate()
        exitcode = proc.returncode
        time.sleep(15)
        logging.debug("Exit msg: {0}".format(exitcode))
        return False
    else :
        return True
    
    """
        TODO: pokusit se upravit, aby se kontroloval exit code scriptu, nastavit timeout. Chyby resit vyjimkou.
    """    
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

import logging
import socket
import subprocess
from configparser import ConfigParser
from subprocess import Popen, PIPE


def list_samba(server_ip, home_folder):
    process = Popen(['./list_samba.sh', server_ip, home_folder], stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()
    sound_sets = output.decode('utf-8').splitlines()[2:]  # . .. Veronika, Zbynek, Ivona

    return sound_sets


def download_sound_files_samba(server_ip, home_folder, sound_set):
    try:
        logging.info("Aktualizace zvukove sady: {0}".format(sound_set))
        process = Popen(['./download_sound_set.sh', server_ip, home_folder, sound_set], stdout=PIPE, stderr=PIPE)
        output, error = process.communicate(timeout=60)

        return process.returncode, output, error

    except subprocess.TimeoutExpired:
        return 1, "timeout", "timeout"


def get_device_ip():
    return socket.gethostbyname(socket.gethostname())


class DeviceInfo:

    def __init__(self):
        self.server_name = ''
        self.area = ''
        self.verbosity = ''
        self.path = ''
        self.soundset = ''
        self.soundset_path = ''
        self.smb_server = ''
        self.smb_home_folder = ''
        self.read_device_config()

    def read_device_config(self):
        # funkce pro načtení konfiguračního souboru
        parser = ConfigParser()
        parser.read('global_config.ini')

        server = parser.sections()[0]
        self.server_name = (parser[server]['name'])
        area = parser.sections()[1]
        self.area = (parser[area]['name'])
        logg = parser.sections()[2]
        self.verbosity = (parser[logg]['verbosity'])
        self.path = (parser[logg]['path'])
        sound = parser.sections()[3]
        self.soundset = (parser[sound]['soundset'])
        self.soundset_path = (parser[sound]['soundset_path'])
        samba = parser.sections()[4]
        self.smb_server = (parser[samba]['server'])
        self.smb_home_folder = (parser[samba]['home_folder'])

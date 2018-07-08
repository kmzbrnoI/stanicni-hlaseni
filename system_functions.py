import logging
import socket
import subprocess
import os
from configparser import ConfigParser
from subprocess import Popen, PIPE


GLOBAL_CONFIG_FILENAME = 'global_config.ini'


class ConfigFileNotFoundError(Exception):
    pass


class ConfigFileBadFormatError(Exception):
    pass


def list_samba(server_ip, home_folder):
    process = Popen(['./list_samba.sh', server_ip, home_folder], stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()
    sound_sets = output.decode('utf-8').splitlines()[2:]  # . .. Veronika, Zbynek, Ivona

    return sound_sets


def download_sound_files_samba(server_ip, home_folder, sound_set):
    try:
        logging.info("Downloading {0}...".format(sound_set))
        process = Popen(['./download_sound_set.sh', server_ip, home_folder, sound_set], stdout=PIPE, stderr=PIPE)
        output, error = process.communicate(timeout=60)

        return process.returncode, output, error

    except subprocess.TimeoutExpired:
        return 1, "timeout", "timeout"


class DeviceInfo:

    def __init__(self):
        """Reads device info from configuration file."""
        if not os.path.isfile(GLOBAL_CONFIG_FILENAME):
            raise ConfigFileNotFoundError("Config file not found: "
                                          "{0}!".format(GLOBAL_CONFIG_FILENAME))

        parser = ConfigParser()
        parser.read(GLOBAL_CONFIG_FILENAME)

        try:
            self.server_name = parser['server']['name']
            self.area = parser['area']['name']
            self.verbosity = parser['logging']['verbosity']
            self.path = parser['logging']['path']
            self.soundset = (parser['sound']['soundset'])
            self.soundset_path = (parser['sound']['soundset_path'])
            self.smb_server = (parser['samba']['server'])
            self.smb_home_folder = (parser['samba']['home_folder'])
        except Exception as e:
            raise ConfigFileBadFormatError("Bad format of config file:"
                                           "{0}!".format(str(e)))

"""
This file defines configuration of a Station Annoucement service.
"""

import os
from configparser import ConfigParser


GLOBAL_CONFIG_FILENAME = 'global_config.ini'


class ConfigFileNotFoundError(Exception):
    pass


class ConfigFileBadFormatError(Exception):
    pass


class DeviceInfo:

    def __init__(self):
        """Reads device info from configuration file."""
        if not os.path.isfile(GLOBAL_CONFIG_FILENAME):
            raise ConfigFileNotFoundError(
                "Config file not found: "
                "{0}!".format(GLOBAL_CONFIG_FILENAME)
            )

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

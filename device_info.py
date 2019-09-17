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
                'Config file not found: '
                '{0}!'.format(GLOBAL_CONFIG_FILENAME)
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
            raise ConfigFileBadFormatError('Bad format of config file:'
                                           '{0}!'.format(str(e)))

    def store(self, filename: str):
        config = ConfigParser()

        config.add_section('server')
        config.set('server', 'name', self.server_name)

        config.add_section('area')
        config.set('area', 'name', self.area)

        config.add_section('logging')
        config.set('logging', 'verbosity', self.verbosity)
        config.set('logging', 'path', self.path)

        config.add_section('sound')
        config.set('sound', 'soundset_path', self.soundset_path)
        config.set('sound', 'soundset', self.soundset)

        config.add_section('samba')
        config.set('samba', 'server', self.smb_server)
        config.set('samba', 'home_folder', self.smb_home_folder)

        with open(filename, 'w') as f:
            config.write(f)

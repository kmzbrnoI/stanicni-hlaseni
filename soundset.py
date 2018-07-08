import logging
import os
from configparser import ConfigParser


DEFAULT_CONFIG_FILENAME = 'config.ini'


class ConfigFileNotFoundError(Exception):
    pass


class ConfigFileBadFormatError(Exception):
    pass


class SoundSet:
    def __init__(self, root, setname):
        self.root = root
        self.load_sound_config(os.path.join(root, setname, DEFAULT_CONFIG_FILENAME))
        logging.info("Soundset loaded from {0}.".format(
            os.path.join(root, setname, DEFAULT_CONFIG_FILENAME)
        ))
        self.hierarchy = self.get_hierarchy(root, self.name)

    def load_sound_config(self, filename):
        parser = ConfigParser()
        if not os.path.isfile(filename):
            raise ConfigFileNotFoundError("Config file not found: "
                                          "{0}!".format(file_path))
        parser.read(filename)

        try:
            self.name = parser.sections()[0]
            self.parent_sound_set = (parser[self.name]['base'])
            self.play_gong = parser.getboolean("sound", "gong")
            self.salutation = parser.getboolean('sound', 'salutation')
            self.train_num = parser.getboolean('sound', 'trainNum')
            self.time = parser.getboolean('sound', 'time')
        except Exception as e:
            raise ConfigFileBadFormatError("Bad format of config file:"
                                           "{0}!".format(str(e)))

    def get_hierarchy(self, root, soundset):
        result = []
        current = soundset

        while current and current not in result:
            result.append(current)
            filename = os.path.join(self.root, current, DEFAULT_CONFIG_FILENAME)

            logging.info("Reading {0}...".format(filename))

            if not os.path.isfile(filename):
                raise ConfigFileNotFoundError("Config file not found: "
                                              "{0}!".format(filename))

            try:
                parser = ConfigParser()
                parser.read(filename)
                current = parser[current]['base']
            except Exception as e:
                raise ConfigFileBadFormatError("Bad format of config file:"
                                               "{0}!".format(str(e)))

        return result

    def assign(self, report):
        """
        Assigns name of the directory to each part of the announcement based
        on non/existence of the file in each directory in the hierarchy.
        """
        result = []
        for r in report:
            for s in self.hierarchy:
                filename = os.path.join(self.root, s, r)
                if os.path.isfile(filename):
                    result.append(filename)
                    break

        # DEBUG
        logging.debug(str(result))

        return result


    def print_sound_config(self):
        # funkce pouze pro správné otestování funkčnosti
        logging.debug("Sound set: ".format(self.sound_set))
        logging.debug("Parent sound set: ".format(self.parent_sound_set))
        logging.debug("Gong: ".format(self.play_gong))
        logging.debug("Salutation: ".format(self.salutation))
        logging.debug("Train number: ".format(self.train_num))
        logging.debug("Time: ".format(self.time))

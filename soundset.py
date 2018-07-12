"""
This file defines SoundSet class which represents a single soundset.
Beware that single soundset includes all parent soundsets in a certain way.
It remeberes whole soundset hierarchy and allows finding sound files in it.

Configuration of a sound set is based on configurations of parent sound sets
too. Confugration in childrens always overwrites configuration in a parent.  If
no configuration is defined, the value of parameter is 'None'.
"""

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

        self.name = None
        self.play_gong = None
        self.salutation = None
        self.train_num = None
        self.time = None

        self.hierarchy = self.load_hierarchy(root, setname)

    def load_sound_config(self, parser):
        """Loads config of a single file in a hierarchy."""
        try:
            if self.name is None:
                self.name = parser.sections()[0]

            if self.play_gong is None and parser.has_option("sound", "gong"):
                self.play_gong = parser.getboolean("sound", "gong")
            if self.salutation is None and parser.has_option("sound", "salutation"):
                self.salutation = parser.getboolean('sound', 'salutation')
            if self.train_num is None and parser.has_option("sound", "trainNum"):
                self.train_num = parser.getboolean('sound', 'trainNum')
            if self.time is None and parser.has_option("sound", "time"):
                self.time = parser.getboolean('sound', 'time')
        except Exception as e:
            raise ConfigFileBadFormatError("Bad format of config file:"
                                           "{0}!".format(str(e)))

    def load_hierarchy(self, root, soundset):
        """
        Loads config baased of all config files in hierarchy. Returns list
        of names of soundsets in hierachy from children to parents.
        """
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
                self.load_sound_config(parser)

                if parser.has_option(current, 'base'):
                    current = parser[current]['base']
                else:
                    current = None
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
        """Debug function."""
        logging.debug("Name: {0}".format(self.name))
        logging.debug("Gong: {0}".format(self.play_gong))
        logging.debug("Salutation: {0}".format(self.salutation))
        logging.debug("Train number: {0}".format(self.train_num))
        logging.debug("Time: {0}".format(self.time))

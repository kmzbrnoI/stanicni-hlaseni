"""
This file defines functions for soundset management.
"""

import subprocess
import os
import logging
from configparser import ConfigParser
import soundset as ss


class SetsListListError(Exception):
    pass


class DownloadError(Exception):
    pass


class SambaNotConfiguredError(Exception):
    pass


def sync(server, home_folder, soundset, soundset_path):
    """
    Downloads current soundset from samba server and all parent soundsets too.
    """
    current = soundset
    loaded = []

    while current:
        logging.debug("Downloading {0}...".format(current))
        _download_sound_set(server, home_folder, current, soundset_path)
        logging.debug("{0} downloaded succesfully.".format(current))

        fn = os.path.join(soundset_path, current, ss.DEFAULT_CONFIG_FILENAME)
        if not os.path.isfile(fn):
            raise ss.ConfigFileNotFoundError("Config file not found: "
                                             "{0}!".format(fn))
        parser = ConfigParser()
        parser.read(fn)
        name = parser.sections()[0]
        loaded.append(current)
        current = parser[name]['base']

        if current in loaded:  # avoid infinite loop when circular reference
            break


def get_samba_sets_list(server, home, soundset_path):
    """Returns list of available soundsets at samba server."""
    process = subprocess.Popen(
        [os.path.abspath('list_samba.sh'), server, home],
        cwd=soundset_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, err = process.communicate()

    if process.returncode != 0:
        raise SetsListListError("Unable to get list of available sets: "
                                "{0}".format(err.decode('utf-8')))

    return output.decode('utf-8').splitlines()[2:]


def get_local_sets_list(root):
    """Returns list of local available soundsets."""
    return [o for o in os.listdir(root)
            if os.path.isdir(os.path.join(root, o)) and o[0] != '.']


def change_set(soundset, soundset_path, server, home_folder):
    if not os.path.isdir(os.path.join(soundset_path, soundset)):
        if not server or not home_folder:
            raise SambaNotConfiguredError('Samba is not configured!')

        sync(server, home_folder, soundset, soundset_path)


def _download_sound_set(server_ip, home_folder, sound_set, soundset_path):
    process = subprocess.Popen(
        [os.path.abspath('download_sound_set.sh'), server_ip, home_folder, sound_set],
        cwd=soundset_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate(timeout=60)

    if process.returncode != 0:
        raise DownloadError('Download error: '
                            '{0}'.format(stderr.decode('utf-8')))

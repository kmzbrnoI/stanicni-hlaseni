"""
This file defines functions for soundset management.
"""

import subprocess
import os
import logging
from configparser import ConfigParser
import soundset as ss
from typing import List


class SetsListListError(Exception):
    pass


class DownloadError(Exception):
    pass


class SambaNotConfiguredError(Exception):
    pass


class RemountError(Exception):
    pass


def sync(server: str, home_folder: str, soundset: str,
         soundset_path: str) -> None:
    """
    Downloads current soundset from samba server and all parent soundsets too.
    """
    current = soundset
    loaded = []

    while current:
        logging.info('Downloading {0}...'.format(current))
        _download_sound_set(server, home_folder, current, soundset_path)
        logging.info('{0} downloaded succesfully.'.format(current))

        fn = os.path.join(soundset_path, current, ss.DEFAULT_CONFIG_FILENAME)
        if not os.path.isfile(fn):
            raise ss.ConfigFileNotFoundError('Config file not found: '
                                             '{0}!'.format(fn))
        parser = ConfigParser()
        parser.read(fn)
        name = parser.sections()[0]
        loaded.append(current)
        current = parser[name]['base']

        if current in loaded:  # avoid infinite loop when circular reference
            break


def get_samba_sets_list(server: str, home: str,
                        soundset_path: str) -> List[str]:
    """Returns list of available soundsets at samba server."""
    process = subprocess.Popen(
        [os.path.abspath('list_samba.sh'), server, home],
        cwd=soundset_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, err = process.communicate()

    if process.returncode != 0:
        raise SetsListListError('Unable to get list of available sets: '
                                '{0}'.format(err.decode('utf-8')))

    return list(output.decode('utf-8').splitlines())[2:]


def get_local_sets_list(root: str) -> List[str]:
    """Returns list of local available soundsets."""
    return [o for o in os.listdir(root)
            if os.path.isdir(os.path.join(root, o)) and o[0] != '.']


def change_set(soundset: str, soundset_path: str, server: str,
               home_folder: str) -> None:
    if not os.path.isdir(os.path.join(soundset_path, soundset)):
        if not server or not home_folder:
            raise SambaNotConfiguredError('Samba is not configured!')

        sync(server, home_folder, soundset, soundset_path)


def _download_sound_set(server_ip: str, home_folder: str, sound_set: str,
                        soundset_path: str) -> None:
    process = subprocess.Popen(
        [
            os.path.abspath('download_sound_set.sh'),
            server_ip,
            home_folder,
            sound_set
        ],
        cwd=soundset_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate(timeout=60)

    if process.returncode != 0:
        raise DownloadError('Download error: '
                            '{0}'.format(stderr.decode('utf-8')))


def is_ro(path: str) -> bool:
    stat = os.statvfs(path)
    return bool(stat.f_flag & os.ST_RDONLY)


def _remount(path: str, mode: str) -> None:
    logging.info('Remounting {0}...'.format(mode))

    process = subprocess.Popen(
        [os.path.abspath(mode + '.sh')],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate(timeout=60)

    if process.returncode != 0:
        raise RemountError('Remount {0} error: '
                           '{1}'.format(mode, stderr.decode('utf-8')))


def remount_ro(path: str) -> None:
    _remount(path, 'ro')


def remount_rw(path: str) -> None:
    _remount(path, 'rw')

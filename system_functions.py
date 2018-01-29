#!/usr/bin/python3

import os
import subprocess


def play_sound(file_name):
    os.system('aplay ' + str(file_name))


def download_sound_files_github():
    clone = "git clone https://github.com/kmzbrnoI/shZvuky"
    os.system(clone)


def download_sound_files_samba(server_ip, home_folder, sound_set):
    subprocess.call(["./download_sound_set.sh", server_ip, home_folder, sound_set]);

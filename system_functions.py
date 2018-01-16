#!/usr/bin/python3

import os


def play_sound(file_name):
    os.system('aplay ' + str(file_name))


def download_sound_files():
    clone = "git clone https://github.com/kmzbrnoI/shZvuky"
    os.system(clone)

"""
This file defines low-level functions for palying sound.
"""

import os
import pygame.mixer


class FileNotFoundError(Exception):
    pass


def play_report(report):
    # Check existence of all files
    for f in report:
        if not os.path.isfile(f):
            raise FileNotFoundError("{0} not found!".format(f))

    _play_report(report)


def _play_report(sound_sequence):
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()

    clock = pygame.time.Clock()
    sounds = [pygame.mixer.Sound(f) for f in sound_sequence]
    for s in sounds:
        s.play()
        channel = s.play()
        while channel.get_busy():
            clock.tick(10)

    pygame.mixer.quit()

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

"""
def define_sound_sequence(self, sound_sequnce):
    Funkce na úpravu pole pro generování finálního zvuku.
    (dle parametru konfiguračního souboru)
    elements_to_remove = []

    for i, sound in enumerate(sound_sequnce):
        if not self.play_gong:
            if "gong" in sound:
                elements_to_remove.append(sound)
        if not self.salutation:
            if "salutation" in sound:
                elements_to_remove.append(sound)
        if not self.train_num:
            if "trainNum" in sound:
                elements_to_remove.append(sound)
        if not self.time:
            if "time" in sound:
                elements_to_remove.append(sound)

    final_sequence = [x for x in sound_sequnce if x not in elements_to_remove]

    return final_sequence
"""

"""
def all_files_exist(self, sound_sequence):
    # funkce zkontroluje zda existuji vsechny soubory, pokud se soubor nenachazi v aktualni zvukove sade,
    # zkusit sadu rodice
    # data v sound_sequence jsou ve formatu /parts/prijel.ogg

    exist = True
    for i, sound in enumerate(sound_sequence):
        if os.path.exists(os.path.join(self.sound_set_path, self.sound_set, sound)):
            sound_sequence[i] = os.path.join(self.sound_set_path, self.sound_set, sound)
        else:
            logging.debug('File not found in %s' % sound)
            if os.path.exists(os.path.join(self.sound_set_path, self.parent_sound_set, sound)):
                sound_sequence[i] = os.path.join(self.sound_set_path, self.parent_sound_set, sound)
                logging.debug("Using file from parent sound set.")
            elif os.path.exists(os.path.join(self.sound_set_path, "default", sound)):
                sound_sequence[i] = os.path.join(self.sound_set_path, "default", sound)
                logging.debug("Using sound from default soundset.")
            else:
                logging.error("File not found!")
                exist = False

    return exist
"""

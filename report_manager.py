#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from configparser import ConfigParser

import pygame.mixer


DEFAULT_CONFIG_FILENAME = 'config.ini'


class ConfigFileNotFoundError(Exception):
    pass


class ConfigFileBadFormatError(Exception):
    pass


class ReportManager:
    def __init__(self, sound_set, sound_set_path, area):
        self.config_file_name = DEFAULT_CONFIG_FILENAME
        self.sound_set = sound_set
        self.parent_sound_set = ''
        self.play_gong = True
        self.salutation = True
        self.train_num = True
        self.time = True
        self.area = area
        self.sound_set_path = sound_set_path
        logging.debug("Soundset loaded from ".format(self.sound_set_path))
        self.load_sound_config()

    def load_sound_config(self):
        # funkce pro načtení konfiguračního souboru
        parser = ConfigParser()
        file_path = os.path.join(
            self.sound_set_path,
            self.sound_set,
            self.config_file_name)

        if not os.path.isfile(file_path):
            raise ConfigFileNotFoundError("Config file not found: "
                                          "{0}!".format(file_path))

        parser.read(file_path)

        try:
            self.sound_set = parser.sections()[0]
            self.parent_sound_set = (parser[self.sound_set]['base'])
            self.play_gong = parser.getboolean("sound", "gong")
            self.salutation = parser.getboolean('sound', 'salutation')
            self.train_num = parser.getboolean('sound', 'trainNum')
            self.time = parser.getboolean('sound', 'time')
        except Exception as e:
            raise ConfigFileBadFormatError("Bad format of config file:"
                                           "{0}!".format(str(e)))

    def print_sound_config(self):
        # funkce pouze pro správné otestování funkčnosti
        logging.debug("Sound set: ".format(self.sound_set))
        logging.debug("Parent sound set: ".format(self.parent_sound_set))
        logging.debug("Gong: ".format(self.play_gong))
        logging.debug("Salutation: ".format(self.salutation))
        logging.debug("Train number: ".format(self.train_num))
        logging.debug("Time: ".format(self.time))

    def define_sound_sequence(self, sound_sequnce):
        """
        Funkce na úpravu pole pro generování finálního zvuku.
        (dle parametru konfiguračního souboru)
        """
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

    @staticmethod
    def play_report(sound_sequence):

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()

        clock = pygame.time.Clock()
        sounds = [pygame.mixer.Sound(f) for f in sound_sequence]
        for s in sounds:
            s.play()
            channel = s.play()
            while channel.get_busy():
                clock.tick(10)

    def create_report(self,
                      sound_sequence):

        redefined_sound_sequence = self.define_sound_sequence(sound_sequence)

        if len(redefined_sound_sequence) > 0:
            # nejdrive otestuji, zda upraveny seznam obsahuje nejake polozky
            if self.all_files_exist(redefined_sound_sequence):
                self.play_report(redefined_sound_sequence)

            else:
                logging.error('File read error!')
        else:
            logging.error("Announcement list is empty!")

    @staticmethod
    def find_audio_number(number):
        sound_set = []

        for position, character in enumerate(reversed(number)):  # jdu od jednotek, abych synchronizoval pozici a číslo

            # pouze pro pro hodnoty 10, 11, 12...
            if (position == 1) and (character == "1"):
                first_char = sound_set[0]
                sound_set[0] = '1' + first_char

            else:
                data = character + ('0' * position)  # vytisknu číslo + počet nul
                sound_set.append(data)

        output_list = []

        for sound in reversed(sound_set):  # nakonec ještě nahrávky vytisknu v opačném pořadí pro správné seřazení
            if int(sound) != 0:  # přetypuji na integer pokud znak není nula, připojím do seznamu
                output_list.append(sound)

        return output_list

    @staticmethod
    def assign_number_directory(input_list):
        output_list = [os.path.join("numbers", "trainNum", (x + ".ogg")) for x in input_list[:-1]]
        last_item = os.path.join("numbers", "trainNum_end", (input_list[-1] + ".ogg"))
        output_list.append(last_item)

        return output_list

    def parse_train_number(self, train_number):

        train_number_len = len(train_number)
        logging.debug("Train number: ".format(train_number))

        if train_number_len % 2 == 0:  # zjistím, jestli je delka čísla vlaku sudá
            first_part, second_part = train_number[:len(train_number) // 2], train_number[len(train_number) // 2:]

            tmp_list = self.find_audio_number(first_part)
            first_list = self.assign_number_directory(tmp_list)

            tmp_list = self.find_audio_number(second_part)
            second_list = self.assign_number_directory(tmp_list)

            first_list += second_list
            return first_list

        if train_number_len < 4:
            tmp_list = self.find_audio_number(train_number)
            output_list = self.assign_number_directory(tmp_list)

            return output_list

        if train_number_len == 5:
            first_part, second_part = train_number[:2], train_number[2:]

            tmp_list = self.find_audio_number(first_part)
            first_list = self.assign_number_directory(tmp_list)

            tmp_list = self.find_audio_number(second_part)
            second_list = self.assign_number_directory(tmp_list)

            first_list += second_list

            return first_list

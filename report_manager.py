import os
import wave
import logging
from configparser import ConfigParser

import pygame.mixer


class ReportManager:
    def __init__(self):
        self.config_file_name = 'config.ini'
        self.report_id = 0
        self.sound_set = ''
        self.parent_sound_set = ''
        self.play_gong = True
        self.salutation = True
        self.train_num = True
        self.time = True
        self.load_sound_config()

    def increment_report_id(self):
        self.report_id += 1

    def get_report_id(self):
        return self.report_id

    def load_sound_config(self):
        # funkce pro načtení konfiguračního souboru
        parser = ConfigParser()
        parser.read(self.config_file_name)

        self.sound_set = parser.sections()[0]
        self.parent_sound_set = (parser[self.sound_set]['base'])
        self.play_gong = (parser.getboolean("sound", "gong"))
        self.salutation = (parser.getboolean('sound', 'salutation'))
        self.train_num = (parser.getboolean('sound', 'trainNum'))
        self.time = (parser.getboolean('sound', 'time'))

    def print_sound_config(self):
        # funkce pouze pro správné otestování funkčnosti
        logging.debug("Budou vyuzity tyto parametry:")
        logging.debug("Zvukova sada: ".format(self.sound_set))
        logging.debug("Rodicovska zvukova sada: ".format(self.parent_sound_set))
        logging.debug("Gong: ".format(self.play_gong))
        logging.debug("Osloveni: ".format(self.salutation))
        logging.debug("Cislo vlaku: ".format(self.train_num))
        logging.debug("Cas: ".format(self.time))

    def define_sound_sequence(self, sound_sequnce):
        # funkce na úpravu pole pro generování finálního zvuku, podle parametru konfiguračního souboru
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
        # funkce zkontroluje zda existuji vsechny soubory, pokud se soubor nenachazi v aktualni zvukove sade, zkusit sadu rodice
        # data v sound_sequence jsou ve formatu /numbers/50.wav

        exist = True
        for i, sound in enumerate(sound_sequence):
            if (os.path.exists(self.sound_set + "/" + sound)):
                sound_sequence[i] = self.sound_set + "/" + sound
            else:
                logging.debug('Nenasel jsem soubor v prirazenem adresari: %s' % sound)
                if (os.path.exists(self.parent_sound_set + "/" + sound)):
                    sound_sequence[i] = self.parent_sound_set + "/" + sound
                    logging.debug("Vyuziji soubor z rodicoskeho adresare...")
                elif (os.path.exists("default/" + sound)):
                    # tahle cast se nakonec asi nebude potreba
                    sound_sequence[i] = "default/" + sound
                    logging.debug("Vyuziji soubor z defaultniho adresare...")
                else:
                    logging.error("Nenasel jsem pozadovany soubor!")
                    exist = False

        return exist

    def merge_wavs(self, sound_sequence, file_name):
        # poskladam zvuky podle potrebne posloupnosti
        data = []

        for sound in sound_sequence:
            w = wave.open(sound, 'rb')
            data.append([w.getparams(), w.readframes(w.getnframes())])
            w.close()

        output = wave.open(file_name, 'wb')
        output.setparams(data[0][0])

        # postpojuji vysledne zvuky
        for sound in range(len(data)):
            output.writeframes(data[sound][1])

        output.close()

    def play_report_ram(self, sound_sequence):
        
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.init()
        
        clock = pygame.time.Clock()
        sounds = [pygame.mixer.Sound(f) for f in sound_sequence]
        for s in sounds:
            s.play()
            channel = s.play()
            while channel.get_busy():
                clock.tick(10)

    def play_report_stream(self, sound_sequence):

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        clock = pygame.time.Clock()
        while len(sound_sequence) > 0:

            pygame.mixer.music.load(sound_sequence.pop(0))
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                clock.tick(1000)

    def create_report(self,
                      sound_sequence):

        redefined_sound_sequence = self.define_sound_sequence(sound_sequence)

        if len(redefined_sound_sequence) > 0:
            # nejdrive otestuji, zda upraveny seznam obsahuje nejake polozky
            if self.all_files_exist(redefined_sound_sequence):
                self.increment_report_id()
                file_name = self.get_report_id()
                # outfile = str(file_name) + ".ogg"
                # self.merge_wavs(redefined_sound_sequence, outfile)
                self.play_report_ram(redefined_sound_sequence)

            else:
                print('Nastala chyba se ctenim souboru...')
        else:
            print("Seznam pro hlaseni neobsahuje zadne polozky!")

    def find_audio_number(self, number):
        sound_set = []

        for position, character in enumerate(reversed(number)):  # jdu od jednotek, abych synchronizoval pozici a číslo

            # pouze pro pro hodnoty 10, 11, 12...
            if ((position == 1) and (character == "1")):
                first_char = sound_set[0]
                sound_set[0] = '1' + first_char

            else:
                data = character + ('0' * position)  # vytisknu číslo + počet nul
                sound_set.append(data)
                
        output_list = []

        for sound in reversed(sound_set):  # nakonec ještě nahrávky vytisknu v opačném pořadí pro správné seřazení
            if int(sound) != 0: # přetypuji na integer pokud znak není nula, připojím do seznamu
                output_list.append(sound)

        return output_list

    def assign_number_directory(self, input_list):
        output_list = ["numbers/trainNum/" + x + ".ogg" for x in input_list[:-1]]
        last_item = "numbers/trainNum_end/" + input_list[-1] + ".ogg"
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

            return (output_list)

        if train_number_len == 5:
            first_part, second_part = train_number[:2], train_number[2:]

            tmp_list = self.find_audio_number(first_part)
            first_list = self.assign_number_directory(tmp_list)

            tmp_list = self.find_audio_number(second_part)
            second_list = self.assign_number_directory(tmp_list)

            first_list += second_list
            
            return first_list



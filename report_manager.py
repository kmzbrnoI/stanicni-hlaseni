import os
import wave
from configparser import ConfigParser


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
        print("Budou vyuzity tyto parametry:")
        print("Zvukova sada: ", self.sound_set)
        print("Rodicovska zvukova sada: ", self.parent_sound_set)
        print("Gong: ", self.play_gong)
        print("Osloveni: ", self.salutation)
        print("Cislo vlaku: ", self.train_num)
        print("Cas: ", self.time)

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
                if "numbers" in sound:
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
                print('Nenasel jsem soubor v prirazenem adresari: %s' % sound)
                if (os.path.exists(self.parent_sound_set + "/" + sound)):
                    sound_sequence[i] = self.parent_sound_set + "/" + sound
                    print("Vyuziji soubor z rodicoskeho adresare...")
                elif (os.path.exists("default/" + sound)):
                    # tahle cast se nakonec asi nebude potreba
                    sound_sequence[i] = "default/" + sound
                    print("Vyuziji soubor z defaultniho adresare...")
                else:
                    print("Nenasel jsem pozadovany soubor!")
                    exist = False

        return exist

    def create_report(self,
                      sound_sequence):

        redefined_sound_sequence = []
        redefined_sound_sequence = self.define_sound_sequence(sound_sequence)

        # print("velikost seznamu: ", len(redefined_sound_sequence))

        if len(redefined_sound_sequence) > 0:
            # nejdrive otestuji, zda upraveny seznam obsahuje nejake polozky
            if self.all_files_exist(redefined_sound_sequence):
                self.increment_report_id()
                file_name = self.get_report_id()
                outfile = str(file_name) + ".wav"

                # poskladam zvuky podle potrebne posloupnosti
                data = []

                for sound in redefined_sound_sequence:
                    w = wave.open(sound, 'rb')
                    data.append([w.getparams(), w.readframes(w.getnframes())])
                    w.close()

                output = wave.open(outfile, 'wb')
                output.setparams(data[0][0])

                # postpojuji vysledne zvuky
                for sound in range(len(data)):
                    output.writeframes(data[sound][1])

                output.close()
            else:
                print('Nastala chyba se ctenim souboru...')
        else:
            print("Seznam pro hlaseni neobsahuje zadne polozky!")

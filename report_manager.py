"""
This file cares about finding proper sounds to announcement.
"""

import logging
import os

import message_parser
from soundset import SoundSet
import report_player


class UnknownMessageTypeError(Exception):
    pass


class TrainSet:
    def __init__(self, message):
        self.station = ''
        self.load_train_set(message)

    def load_train_set(self, message):
        parsed = message_parser.parse(message, [';'])

        self.train_number = parsed[0]
        self.train_type = parsed[1]
        self.railway = parsed[2]
        self.start_station = parsed[3]
        self.final_station = parsed[4]

        self.arrival_time = parsed[5] if len(parsed) > 5 else ''
        self.departure_time = parsed[6] if len(parsed) > 6 else ''

    def print_info(self):
        logging.debug("Train number: {0}".format(self.train_number))
        logging.debug("Train type: {0}".format(self.train_type))
        logging.debug("Railway: {0}".format(self.railway))
        logging.debug("Start station: {0}".format(self.start_station))
        logging.debug("Final station: {0}".format(self.final_station))
        logging.debug("Arrival time: {0}".format(self.arrival_time))
        logging.debug("Departure time: {0}".format(self.departure_time))
        logging.debug("Station: {0}".format(self.departure_time))


class ReportManager:

    def __init__(self, device_info):
        self.area = device_info.area
        self.soundset = SoundSet(device_info.soundset_path, device_info.soundset)

    def process_trainset_message(self, parsed):
        message_type = parsed[2].lower()
        train_set = TrainSet(parsed[3])
        train_set.print_info()

        # Prepare common part of announcement
        report = []
        if self.soundset.salutation:
            report.append(os.path.join("salutation", "prosim_pozor.ogg"))
        report.append(self._get_traintype_file(train_set.train_type))

        if self.soundset.train_num:
            report += self._parse_train_number(train_set.train_number)

        if message_type == "prijede":
            report += self._prijede(train_set)
        elif message_type == "odjede":
            report += self._odjede(train_set)
        elif message_type == "projede":
            report += self._projede(train_set)
        else:
            raise UnknownMessageTypeError("This type of announcement is not supported!")

        report_player.play_report(self.soundset.assign(report))

    def nesahat(self):
        return [os.path.join("spec", "nedotykejte_se_prosim_vystavenych_modelu.ogg")]

    def posun(self):
        return [os.path.join("spec", "prosim_pozor.ogg"), os.path.join("spec", "probiha_posun.ogg")]

    def play_raw_report(self, report):
        report_player.play_report(self.soundset.assign(report))

    def _get_traintype_file(self, train_type):
        if self.soundset.train_num:
            return os.path.join("trainType", train_type + "_cislo.ogg")
        else:
            return os.path.join("trainType", train_type + ".ogg")

    def _get_time(self, train_set, action):
        report = []
        hours = ''
        minutes = ''

        if action == "prijede":
            report.append(os.path.join("parts", "pravidelny_prijezd.ogg"))
            hours, minutes = train_set.arrival_time.split(":")

        elif action == "odjede":
            report.append(os.path.join("parts", "pravidelny_odjezd.ogg"))
            hours, minutes = train_set.departure_time.split(":")

        hours = os.path.join("time", "hours", (hours.lstrip("0") + ".ogg"))  # odstraneni levostrannych nul (napr. 09 minut)
        minutes = os.path.join("time", "minutes", (minutes.lstrip("0") + ".ogg"))
        report.append(hours)
        report.append(minutes)

        return report

    def _get_railway_file(self, railway, action):
        # This only processes railways <=19!
        if action == 'prijede':
            return os.path.join("numbers", "arrive_railway", railway + ".ogg")
        elif action == 'odjede':
            return os.path.join("numbers", "leave_railway", railway + ".ogg")
        else:
            return os.path.join("numbers", "railway", railway + ".ogg")

    def _prijede(self, train_set):
        report = []

        # pravidelny prijezd 22 hodiny 23 minuty
        if (train_set.arrival_time != '') and self.soundset.time:
            report += _get_time(train_set, "prijede")

        report.append(os.path.join("parts", "prijede.ogg"))
        report.append(os.path.join("parts", "na_kolej.ogg"))
        report.append(self._get_railway_file(train_set.railway, 'prijede'))

        if self.area not in train_set.final_station:
            report.append(os.path.join("parts", "vlak_dale_pokracuje_ve_smeru.ogg"))
            report.append(os.path.join("stations", train_set.final_station))
        else:
            report.append(os.path.join("parts", "vlak_zde_jizdu_konci.ogg"))
            report.append(os.path.join("parts", "prosime_cestujici_aby_vystoupili.ogg"))

        return report

    def _odjede(self, train_set):
        report = []
        report.append(os.path.join("parts", "ve_smeru.ogg"))
        report.append(os.path.join("stations", train_set.final_station))

        if (train_set.departure_time != '') and (self.soundset.time):
            report += _get_time(train_set, "odjede")

        report.append(os.path.join("parts", "odjede.ogg"))
        report.append(os.path.join("parts", "z_koleje.ogg"))

        report.append(train_set.railway)

        return report

    def _projede(self, train_set):
        raise UnknownMessageError(Exception)

    def _parse_train_number(self, train_number):
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

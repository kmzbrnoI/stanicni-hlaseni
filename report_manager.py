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

    def __str__(self):
        return ("Train number: {0}\n".format(self.train_number) +
                "Train type: {0}\n".format(self.train_type) +
                "Railway: {0}\n".format(self.railway) +
                "Start station: {0}\n".format(self.start_station) +
                "Final station: {0}\n".format(self.final_station) +
                "Arrival time: {0}\n".format(self.arrival_time) +
                "Departure time: {0}\n".format(self.departure_time) +
                "Station: {0}".format(self.departure_time))

    __repr__ = __str__


class ReportManager:

    def __init__(self, device_info):
        self.area = device_info.area
        self.soundset = SoundSet(device_info.soundset_path, device_info.soundset)

    def process_trainset_message(self, parsed):
        message_type = parsed[2].lower()
        train_set = TrainSet(parsed[3])

        # Prepare common part of announcement
        report = []
        if self.soundset.salutation:
            report.append(os.path.join("salutation", "prosim_pozor"))
        report.append(self._get_traintype_file(train_set.train_type))

        if self.soundset.train_num and train_set.train_number:
            report += self._parse_train_number(train_set.train_number)

        if message_type == "prijede":
            report += self._prijede(train_set)
        elif message_type == "odjede":
            report += self._odjede(train_set)
        elif message_type == "projede":
            report += self._projede(train_set)
        else:
            raise UnknownMessageTypeError("This type of announcement is not supported!")

        report_player.play_report(self.soundset.assign(self.add_suffix(report)))

    def nesahat(self):
        return [os.path.join("spec", "nedotykejte_se_prosim_vystavenych_modelu")]

    def posun(self):
        return [os.path.join("spec", "prosim_pozor"), os.path.join("spec", "probiha_posun")]

    def play_raw_report(self, report):
        report_player.play_report(self.soundset.assign(self.add_suffix(report)))

    def add_suffix(self, report):
        return map(lambda s: s + '.ogg', report)

    def _get_traintype_file(self, train_type):
        if self.soundset.train_num:
            return os.path.join("trainType", train_type + "_cislo")
        else:
            return os.path.join("trainType", train_type + "")

    def _get_time(self, time):
        """
        Converts time to list of sounds.
        Example of time: '9:46'.
        """
        hours, minutes = time.split(':')

        return [
            os.path.join("time", "hours", hours.lstrip("0")),
            os.path.join("time", "minutes", minutes.lstrip("0"))
        ]

    def _get_railway_file(self, railway, action):
        # This only processes railways <=19!
        if action == 'prijede':
            return os.path.join("numbers", "arrive_railway", railway + "")
        elif action == 'odjede':
            return os.path.join("numbers", "leave_railway", railway + "")
        else:
            return os.path.join("numbers", "railway", railway + "")

    def _prijede(self, train_set):
        report = []

        if train_set.start_station:
            report.append(os.path.join("parts", "ze_smeru"))
            report.append(os.path.join("stations", train_set.start_station))

        report.append(os.path.join("parts", "prijede"))
        report.append(os.path.join("parts", "na_kolej"))
        report.append(self._get_railway_file(train_set.railway, 'prijede'))

        if self.area == train_set.final_station:
            report.append(os.path.join("parts", "vlak_zde_jizdu_konci"))
            report.append(os.path.join("parts", "prosime_cestujici_aby_vystoupili"))
        else:
            report.append(os.path.join("parts", "vlak_dale_pokracuje_ve_smeru"))
            report.append(os.path.join("stations", train_set.final_station))
            if train_set.departure_time and self.soundset.time:
                report.append(os.path.join("parts", "pravidelny_odjezd"))
                report += self._get_time(train_set.departure_time)

        return report

    def _odjede(self, train_set):
        report = []
        report.append(os.path.join("parts", "ve_smeru"))
        report.append(os.path.join("stations", train_set.final_station))

        if (train_set.departure_time != '') and (self.soundset.time):
            report += _get_time(train_set, "odjede")

        report.append(os.path.join("parts", "odjede"))
        report.append(os.path.join("parts", "z_koleje"))

        report.append(train_set.railway)

        return report

    def _projede(self, train_set):
        raise UnknownMessageError(Exception)

    def _parse_train_number(self, train_number):
        train_number_len = len(train_number)
        logging.debug("Train number: {0}".format(train_number))

        if train_number_len % 2 == 0:  # zjistím, jestli je delka čísla vlaku sudá
            first_part, second_part = train_number[:len(train_number) // 2], train_number[len(train_number) // 2:]

            tmp_list = self._find_audio_number(first_part)
            first_list = self._assign_number_directory(tmp_list)

            tmp_list = self._find_audio_number(second_part)
            second_list = self._assign_number_directory(tmp_list)

            first_list += second_list
            return first_list

        if train_number_len < 4:
            tmp_list = self._find_audio_number(train_number)
            output_list = self._assign_number_directory(tmp_list)

            return output_list

        if train_number_len == 5:
            first_part, second_part = train_number[:2], train_number[2:]

            tmp_list = self._find_audio_number(first_part)
            first_list = self._assign_number_directory(tmp_list)

            tmp_list = self._find_audio_number(second_part)
            second_list = self._assign_number_directory(tmp_list)

            first_list += second_list

            return first_list

    @staticmethod
    def _find_audio_number(number):
        """
        This function translates number to sounds.
        It returns list of sounds to be spelled.
        """
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
    def _assign_number_directory(input_list):
        out = [os.path.join("numbers", "trainNum", x) for x in input_list[:-1]]
        out.append(os.path.join("numbers", "trainNum_end", input_list[-1]))
        return out

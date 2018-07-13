"""
This file defines ReportManager which cares about building announcement based
on data received from hJOPserver.
"""

import logging
import os

from soundset import SoundSet
from trainset import TrainSet
import report_player


class UnknownMessageTypeError(Exception):
    pass


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
            report.append(os.path.join("salutation", "vazeni_cestujici"))
        report.append(self._get_traintype_file(train_set.train_type))

        if self.soundset.train_num and train_set.train_number:
            report += self._parse_train_number(train_set.train_number)

        if message_type == "prijede":
            if train_set.final_station == self.area:
                return  # do not play 'arrives' in final station
            report += self._prijede(train_set)
        elif message_type == "odjede":
            report += self._odjede(train_set)
        elif message_type == "projede":
            report += self._projede(train_set)
        else:
            raise UnknownMessageTypeError("This type of announcement is not supported!")

        report_player.play_report(self.soundset.assign(self.add_suffix(report)))

    def process_spec_message(self, special_type):
        if special_type == 'POSUN':
            self.play_raw_report([
                os.path.join("spec", "prosim_pozor"),
                os.path.join("spec", "nevstupujte_prosim_do_kolejiste"),
                os.path.join("parts", "pause"),
                os.path.join("spec", "probiha_posun"),
            ])

        elif special_type == 'NESAHAT':
            self.play_raw_report([
                os.path.join("salutation_end", "vazeni_navstevnici"),
                os.path.join("spec", "nedotykejte_se_prosim_vystavenych_modelu"),
            ])

        else:
            self.play_raw_report([os.path.join("spec", special_type)])

    def play_raw_report(self, report):
        report_player.play_report(self.soundset.assign(self.add_suffix(report)))

    def _prijede(self, train_set):
        report = []

        if train_set.start_station:
            report.append(os.path.join("parts", "ze_smeru"))
            report.append(os.path.join("stations", train_set.start_station))

        if train_set.final_station:
            report.append(os.path.join("parts", "ve_smeru"))
            report.append(os.path.join("stations", train_set.final_station))

        report.append(os.path.join("parts", "prijede"))
        report.append(os.path.join("parts", "na_kolej"))
        report.append(os.path.join("numbers", "railway_end", train_set.railway))

        if train_set.departure_time and self.soundset.time:
            report.append(os.path.join("parts", "pause"))
            report.append(os.path.join("parts", "pravidelny_odjezd"))
            report += self._get_time(train_set.departure_time, end=True)

        return report

    def _odjede(self, train_set):
        report = []

        if train_set.final_station:
            report.append(os.path.join("parts", "ve_smeru"))
            report.append(os.path.join("stations", train_set.final_station))

        if train_set.departure_time and self.soundset.time:
            report.append(os.path.join("parts", "pravidelny_odjezd"))
            report += self._get_time(train_set.departure_time)

        report.append(os.path.join("parts", "odjede"))
        report.append(os.path.join("parts", "z_koleje"))

        report.append(os.path.join("numbers", "leave_railway", train_set.railway))

        return report

    def _projede(self, train_set):
        raise UnknownMessageError(Exception)

    def _get_traintype_file(self, train_type):
        if self.soundset.train_num:
            return os.path.join("trainType", train_type + "_cislo")
        else:
            return os.path.join("trainType", train_type)

    @staticmethod
    def add_suffix(report):
        return map(lambda s: s + '.ogg', report)

    @staticmethod
    def _get_time(time, end=False):
        """
        Converts time to list of sounds.
        Example of time: '9:46'.
        """
        hours, minutes = time.split(':')

        return [
            os.path.join("time", "hours", hours.lstrip("0")),
            os.path.join("time", "minutes" +
                         ('_end' if end else ''), minutes.lstrip("0"))
        ]

    def _parse_train_number(self, train_number):
        train_number_len = len(train_number)
        logging.debug("Train number: {0}".format(train_number))

        if train_number_len % 2 == 0:
            first_part, second_part = (
                train_number[:len(train_number) // 2],
                train_number[len(train_number) // 2:]
            )

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

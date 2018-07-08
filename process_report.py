#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

import message_parser


class UnknownMessageError(Exception):
    pass


class TrainSet:
    def __init__(self, message):
        self.train_number = ''
        self.train_type = ''
        self.railway = ''
        self.start_station = ''
        self.final_station = ''
        self.arrival_time = ''
        self.departure_time = ''
        self.station = ''
        self.load_train_set(message)

    def load_train_set(self, message):
        self.train_number = message[0]
        self.train_type = message[1]
        self.railway = message[2]
        self.start_station = message[3]
        self.final_station = message[4]

        self.arrival_time = message[5] if len(message) > 5 else ''
        self.departure_time = message[6] if len(message) > 6 else ''

    def print_info(self):
        logging.debug("Train number: {0}".format(self.train_number))
        logging.debug("Train type: {0}".format(self.train_type))
        logging.debug("Railway: {0}".format(self.railway))
        logging.debug("Start station: {0}".format(self.start_station))
        logging.debug("Final station: {0}".format(self.final_station))
        logging.debug("Arrival time: {0}".format(self.arrival_time))
        logging.debug("Departure time: {0}".format(self.departure_time))
        logging.debug("Station: {0}".format(self.departure_time))


def process_message(message, rm):
    # ziskanou zpravu nejdrive celou naparsuji
    parsed_message = message_parser.parse(message, ";")

    last_item = parsed_message.pop()

    parsed_message.append(last_item)

    # ziskam typ hlaseni
    message_type = parsed_message[2].lower()

    # naparsuji soupravu
    train_set = _parse_train_set(parsed_message)

    # k naparsovanym datum pridam cesty k souborum
    train_set = _join_path(rm, train_set, message_type)

    # pripravim si spolecnou cast hlaseni
    report = _prepare_report(rm, train_set)
    train_set.print_info()

    if message_type == "prijede":
        _prijede(report, rm, train_set)
    elif message_type == "odjede":
        _odjede(report, rm, train_set)
    elif message_type == "projede":
        _projede(report, rm, train_set)
    else:
        logging.error("This type of announcement is not supported!")
        # raise UnknownMessageTypeError("Neznamy typ zpravy.")

def _join_path(rm, train_set, action):
    if rm.train_num:
        train_set.train_type = os.path.join("trainType", train_set.train_type + "_cislo.ogg")
    else:
        train_set.train_type = os.path.join("trainType", train_set.train_type + ".ogg")


    if action == 'prijede' :
        train_set.railway = os.path.join("numbers", "arrive_railway", train_set.railway + ".ogg")
    elif action == 'odjede' :
        train_set.railway = os.path.join("numbers", "leave_railway", train_set.railway + ".ogg")
    else :
        train_set.railway = os.path.join("numbers", "railway", train_set.railway + ".ogg")


    train_set.start_station = os.path.join("stations", train_set.start_station + ".ogg")
    train_set.final_station = os.path.join("stations", train_set.final_station + ".ogg")

    return train_set


def _parse_train_set(message):
    """naparsuji data a ulozim do TrainSet"""
    train_set_data = message_parser.parse(message[3], ";")
    train_set = TrainSet(train_set_data)
    train_set.print_info()

    return train_set


def _prepare_report(rm, train_set):
    report_list = [os.path.join("salutation", "prosim_pozor.ogg"), train_set.train_type]

    report_list += rm.parse_train_number(train_set.train_number)

    return report_list

def _prepare_time(train_set, action):
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


def _prijede(report, rm, train_set):
    # pravidelny prijezd 22 hodiny 23 minuty
    if (train_set.arrival_time != '') and rm.time:
        report += _prepare_time(train_set, "prijede")

    report.append(os.path.join("parts", "prijede.ogg"))
    report.append(os.path.join("parts", "na_kolej.ogg"))
    report.append(train_set.railway)

    if (rm.area + ".") not in train_set.final_station:  # v tuto chvili uz mam v promennych ulozene cele cesty proto "."
        report.append(os.path.join("parts", "vlak_dale_pokracuje_ve_smeru.ogg"))
        report.append(train_set.final_station)
    else:
        report.append(os.path.join("parts", "vlak_zde_jizdu_konci.ogg"))
        report.append(os.path.join("parts", "prosime_cestujici_aby_vystoupili.ogg"))

    rm.create_report(report)


def _odjede(report, rm, train_set):
    report.append(os.path.join("parts", "ve_smeru.ogg"))
    report.append(train_set.final_station)

    if (train_set.departure_time != '') and rm.time:
        report += _prepare_time(train_set, "odjede")

    report.append(os.path.join("parts", "odjede.ogg"))
    report.append(os.path.join("parts", "z_koleje.ogg"))

    report.append(train_set.railway)

    rm.create_report(report)


def _projede(report, rm, train_set):
    raise UnknownMessageError(Exception)


def nesahat(rm):
    report = [os.path.join("spec", "nedotykejte_se_prosim_vystavenych_modelu.ogg")]
    rm.create_report(report)


def posun(rm):
    report = [os.path.join("spec", "prosim_pozor.ogg"), os.path.join("spec", "probiha_posun.ogg")]
    rm.create_report(report)


def _parse_message(message):
    # metoda prochází zadanou zprávu a postupně na ni volá metodu parse()

    for item in message:  # projdu jednotlivé části zprávy

        parse_item = False

        for character in item:  # postupně prohledám jednotlivé znaky
            # pokud najdu ve zprávě středník, ukončuji cyklus a do parse_item uložím True
            if ';' in character:
                parse_item = True
                break

        if parse_item:

            item = message_parser.parse(item, ";")

            # rekurzivní volání pro vnořené objekty
            parsed_item = _parse_message(item)

            if parsed_item is not None:
                return message[:-1] + parsed_item
            else:
                return message[:-1] + item

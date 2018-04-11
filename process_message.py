import message_parser
import report_manager
import system_functions


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
        print("Train number:", self.train_number)
        print("Train type: ", self.train_type)
        print("Railway: ", self.railway)
        print("Start station: ", self.start_station)
        print("Final station: ", self.final_station)
        print("Arrival time: ", self.arrival_time)
        print("Departure time: ", self.departure_time)


def join_path(train_set):
    train_set.train_type = "trainType/" + train_set.train_type + "_cislo.ogg"
    train_set.railway = "numbers/railway/" + train_set.railway + ".ogg"
    train_set.start_station = "stations/" + train_set.start_station + ".ogg"
    train_set.final_station = "stations/" + train_set.final_station + ".ogg"

    return train_set


def parse_train_set(message):
    train_set_data = message_parser.parse(message[3], ";")
    train_set = TrainSet(train_set_data)
    train_set.print_info()

    return train_set


def prepare_report(train_set):
    rm = report_manager.ReportManager()
    report_list = ["salutation/vazeni_cestujici.ogg", "salutation/prosim_pozor.ogg", train_set.train_type]

    report_list += rm.parse_train_number(train_set.train_number)

    return report_list


def process_message(message):
    parsed_message = message_parser.parse(message, ";")

    last_item = parsed_message.pop()

    last_item = last_item.replace("\n", "")
    last_item = last_item.replace("\r", "")

    parsed_message.append(last_item)

    message_type = parsed_message[2].lower()

    train_set = parse_train_set(parsed_message)

    train_set = join_path(train_set)

    report = prepare_report(train_set)

    if message_type == "prijede":
        prijede(report, train_set)
    elif message_type == "odjede":
        prijede(report, train_set)
    elif message_type == "projede":
        projede(message)
    elif message_type == "sync":
        sync(message)
    elif message_type == "change-set":
        change_set(message)
    elif message_type == "sets-list":
        sets_list(message)
    else:
        print("Zprava neni naimplementovana...")
        # raise UnknownMessageTypeError("Neznamy typ zpravy.")


def prepare_time(train_set, action):
    report = []
    hours = ''
    minutes = ''

    if action == "prijede":
        report.append("parts/pravidelny_prijezd.ogg")
        hours, minutes = train_set.arrival_time.split(":")

    elif action == "odjede":
        report.append("parts/pravidelny_odjezd.ogg")
        hours, minutes = train_set.departure_time.split(":")

    hours = "time/hours/" + hours + ".ogg"
    minutes = "time/minutes/" + minutes + ".ogg"
    report.append(hours)
    report.append(minutes)

    return report


def prijede(report, train_set):
    # číslo;typ;kolej;výchozí stanice;cílová stanice;/čas příjezdu/;/čas odjezdu/
    # 608522;Os;1;Zd;Oc;9:22;9:25

    # Ku', 'SH', 'ODJEDE', '504220', 'Os', '1', 'Bs', 'Ku'

    rm = report_manager.ReportManager()

    report.append("parts/ze_smeru.ogg")

    report.append(train_set.start_station)

    train_set.arrival_time = "22:23"
    # pravidelny prijezd 22 hodiny 23 minuty
    if (train_set.arrival_time != '') and rm.time:
        report += prepare_time(train_set, "prijede")

    report.append("parts/vlak_dale_pokracuje_ve_smeru.ogg")

    report.append(train_set.final_station)

    report.append("parts/prijede.ogg")
    report.append("parts/na_kolej.ogg")

    report.append(train_set.railway)

    rm.create_report(report)


def odjede(report, train_set):
    rm = report_manager.ReportManager()

    report.append("parts/ze_smeru.ogg")

    report.append(train_set.start_station)

    report.append("parts/vlak_dale_pokracuje_ve_smeru.ogg")

    report.append(train_set.final_station)

    # pravidelny odjezd 22 hodiny 23 minuty
    train_set.departure_time = "22:23"

    if (train_set.departure_time != '') and rm.time:
        report += prepare_time(train_set, "odjede")

    report.append("parts/odjede.ogg")
    report.append("parts/z_koleje.ogg")

    report.append(train_set.railway)

    rm.create_report(report)


def projede(message):
    print()


def spec(message):
    print()


def sync(message):
    info_message = "Ku" + ";SH;SYNC;STARTED;\n"
    socket.send(info_message.encode('UTF-8')) 

    # TODO: bude stahovat všechny zvukové sady?

    sound_set = "Veronika"
    system_functions.download_sound_files_samba("10.30.137.105", "share", sound_set)

    info_message = "Ku" + ";SH;SYNC;DONE;\n"
    socket.send(info_message.encode('UTF-8'))


def change_set(message):
    print()


def sets_list(message):
    print()


def parse_message(message):
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
            parsed_item = parse_message(item)

            if parsed_item is not None:
                return message[:-1] + parsed_item
            else:
                return message[:-1] + item

import message_parser
import report_manager


class UnknownMessageError(Exception):
    pass


def process_message(message):
    message = parse_message(message)

    message_type = message[2].lower()

    # print("Type:", message_type)

    if message_type == "prijede":
        prijede(message)
    elif message_type == "odjede":
        odjede(message)
    elif message_type == "projede":
        projede(message)
    elif message_type == "sync":
        sync(message)
    elif message_type == "change-set":
        change_set(message)
    elif message_type == "sets-list":
        sets_list(message)
    else:
        raise UnknownMessageTypeError("Neznamy typ zpravy.")


def prijede(message):
    rm = report_manager.ReportManager()

    report_list = []

    train_number = message[3]
    train_type = "trainType/" + message[4] + ".ogg"
    action = message[2].lower() + ".ogg"

    report_list.append("salutation/vazeni_cestujici.ogg")
    report_list.append("salutation/prosim_pozor.ogg")

    report_list.append(train_type)

    report_list += rm.parse_train_number(train_number)

    report_list.append(action)


def odjede(message):
    print()


def projede(message):
    print()


def spec(message):
    print()


def sync(message):
    print()


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
            if (';') in character:
                parse_item = True
                break

        if parse_item:

            item = message_parser.parse(item, ";")

            # rekurzivní volání pro vnořené objekty
            try:
                # zkusím zavolat rekurzi
                return message[:-1] + parse_message(item)

            except Exception as e:
                # pokud se vrátí vyjímka, vím, že jsem na konci parsovani
                return message[:-1] + item


#process_message(["Zd;SH;PRIJEDE;{504351;Os;7b;Zd;Klb}"])

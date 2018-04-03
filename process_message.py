import message_parser
import report_manager
import time


class UnknownMessageError(Exception):
    pass


def process_message(message):
    print("Zpracovavam: ", message)
    
    message = parse_message(message)

    last_item = message.pop()

    last_item = last_item.replace("\n", "")
    last_item = last_item.replace("\r", "")

    message.append(last_item)
    
    message_type = message[2].lower()

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
    #číslo;typ;kolej;výchozí stanice;cílová stanice;/čas příjezdu/;/čas odjezdu/
    #608522;Os;1;Zd;Oc;9:22;9:25
    
    #Ku', 'SH', 'ODJEDE', '504220', 'Os', '1', 'Bs', 'Ku'
    rm = report_manager.ReportManager()

    report_list = []

    train_number = message[3]
    train_type = "trainType/" + message[4] + "_cislo.ogg"

    railway = "numbers/railway_end/" + message[5] + ".ogg"

    action = message[2].lower() + ".ogg"

    from_station = "stations/" + message[6] + ".ogg"

    to_station = "stations/" + message[7] + ".ogg" 

    report_list.append("salutation/vazeni_cestujici.ogg")
    report_list.append("salutation/prosim_pozor.ogg")

    report_list.append(train_type)

    report_list += rm.parse_train_number(train_number)
        
    report_list.append("parts/ze_smeru.ogg")

    report_list.append(from_station)
    
    report_list.append("parts/vlak_dale_pokracuje_ve_smeru.ogg")   
    
    report_list.append(to_station)
    report_list.append("parts/prijede.ogg")

    report_list.append("parts/na_kolej.ogg")
    
    report_list.append(railway)

    rm.create_report(report_list)


def odjede(message):
    #Ku', 'SH', 'ODJEDE', '504220', 'Os', '1', 'Bs', 'Ku'
    rm = report_manager.ReportManager()

    report_list = []

    train_number = message[3]
    train_type = "trainType/" + message[4] + "_cislo.ogg"

    railway = "numbers/railway_end/" + message[5] + ".ogg"

    action = message[2].lower() + ".ogg"

    from_station = "stations/" + message[6] + ".ogg"

    to_station = "stations/" + message[7] + ".ogg" 

    report_list.append("salutation/vazeni_cestujici.ogg")
    report_list.append("salutation/prosim_pozor.ogg")

    report_list.append(train_type)

    report_list += rm.parse_train_number(train_number)
        
    report_list.append("parts/ze_smeru.ogg")

    report_list.append(from_station)
    
    report_list.append("parts/vlak_dale_pokracuje_ve_smeru.ogg")   
    
    report_list.append(to_station)
    report_list.append("parts/odjede.ogg")

    report_list.append("parts/z_koleje.ogg")
    
    report_list.append(railway)

    rm.create_report(report_list)

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



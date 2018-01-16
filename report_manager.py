import os
import wave


def all_files_exist(sound_sequence):
    exist = True
    for sound in sound_sequence:
        if not (os.path.exists(sound)):
            print('Nenasel jsem soubor: %s' % sound)
            exist = False

    return exist


def create_report(sound_sequence,
                  file_name):  # funci predam posloupnost zvuku, ktere ziskam od serveru a nazev vysledneho souboru

    if (all_files_exist(sound_sequence)):

        outfile = str(file_name) + ".wav"

        # poskladam zvuky podle potrebne posloupnosti
        data = []

        for sound in sound_sequence:
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

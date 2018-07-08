"""
This file defines functions for soundset management.
"""

import subprocess
import os


class SetsListListError(Exception):
    pass


def sync(self, parsed):
    # Vytvorim si docasny report_manager
    tmp_rm = report_manager.ReportManager(self.device_info.soundset, self.device_info.area)
    logging.debug("Default set: {0}".format(self.device_info.soundset))

    # Vylistuji sambu a ziskam dostupne sady

    sound_sets = system_functions.list_samba(self.device_info.smb_server, self.device_info.smb_home_folder)
    logging.debug("Available sets: {0}".format(sound_sets))

    updated = []

    # Oznamim serveru aktualizaci zvukovych sad

    info_message = self.device_info.area + ";SH;SYNC;STARTED;"
    self._send(info_message)

    print(tmp_rm.sound_set)
    while True:
        if (tmp_rm.sound_set in sound_sets) and (tmp_rm.sound_set not in updated):

            logging.debug("Downloading {0}...".format(tmp_rm.sound_set))

            # aktualizace zvukové sady, podle config.ini
            return_code, output, error = system_functions.download_sound_files_samba(
                self.device_info.smb_server,
                self.device_info.smb_home_folder,
                str.strip(tmp_rm.sound_set))

            if str(return_code) == '0':
                logging.debug("{0} downloaded succesfully.".format(tmp_rm.sound_set))
                updated.append(tmp_rm.sound_set)

                if tmp_rm.parent_sound_set in updated:
                    logging.debug("Parent sound set for {0} is downloaded. ({1})".format(tmp_rm.sound_set,
                                                                                         tmp_rm.parent_sound_set))
                    break
                else:
                    tmp_rm = report_manager.ReportManager(tmp_rm.parent_sound_set, self.device_info.area)
                    tmp_rm.load_sound_config()
                    logging.debug("{0} required.".format(tmp_rm.sound_set))

            else:
                # nastala chyba pri aktualizaci zvukove sady
                logging.debug("Non-return code when downloading {0}".format(tmp_rm.sound_set))
                break

        else:
            logging.debug("Downloading finished.")
            break

    version = "1.0"

    return_code = str(return_code)

    if return_code == '0':
        logging.info("Soundset update done..")
        info_message = self.device_info.area + ";SH;SYNC;DONE;" + tmp_rm.sound_set + ";" + version + "\n"
    elif return_code == '99':
        logging.info("Soundset update error: {0} not found on server!".format(
            tmp_rm.sound_set))
        info_message = self.device_info.area + ";SH;SYNC;ERR;" + version + ";" + str(error)
    else:
        logging.error("Soundset update error!")
        info_message = self.device_info.area + ";SH;SYNC;ERR;" + version + ";" + str(error)

    self._send(info_message)


def get_samba_sets_list(server, home):
    process = subprocess.Popen(
        ['./list_samba.sh', server, home],
        stdout=PIPE,
        stderr=PIPE
    )
    output, err = process.communicate()

    if process.return_code != 0:
        raise SetsListListError("Unable to get list of available sets: "
                                "{0}".format(err.decode('utf-8')))

    return output.decode('utf-8').splitlines()[2:]


def get_local_sets_list(root):
    return [o for o in os.listdir(root)
            if os.path.isdir(os.path.join(root, o)) and o[0] != '.']


def _change_set(self, parsed):
    sound_set = parsed[3]

    if path.isdir('./' + sound_set):  # TODO: refactor!
        self.rm.sound_set = sound_set
        self.rm.load_sound_config()
        info_message = self.device_info.area + ";SH;CHANGE-SET;OK;"
    else:
        info_message = self.device_info.area + ";SH;CHANGE-SET;ERR;SET_NOT_AVAILABLE"

    self._send(info_message)


def _download_sound_files_samba(server_ip, home_folder, sound_set):
    try:
        logging.info("Downloading {0}...".format(sound_set))
        process = Popen(['./download_sound_set.sh', server_ip, home_folder, sound_set], stdout=PIPE, stderr=PIPE)
        output, error = process.communicate(timeout=60)

        return process.returncode, output, error

    except subprocess.TimeoutExpired:
        return 1, "timeout", "timeout"

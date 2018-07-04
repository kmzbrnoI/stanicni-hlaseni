# Station Announcement

Station announcements is client-based application. It is based on commands from
hJOPserver. It is a simulation of station announcements that you know from the
train stations. This project mainly aims on Raspberry Pi 3 with speaker and
WiFi located in every station playing the sound. Thus, once the application is
installed, it requires no further control from SSH.

## Installation

 1. Clone this repository.
 2. Install packages from `requirements.txt`.
 3. Run `make all`. This will create `global_config.ini` file.
 4. Edit `global_config.ini` according to your railway.
 5. Optional: run `make install` to install station announcement as a systemd
    service.
 6. Clone sound sets into `shZvuky` folder (transfer raw files or clone
    via git-lfs, see `install_lfs.sh`).
 7. Optional: configure WiFi (see `wpa_supplicant.conf`).
 8. Optional: make system read-only via
    [this script](https://github.com/ways/rpi-readonly).

To uninstall a systemd service, run `make uninstall`.

*Note*: `make install` and `make uninstall` require access to *systemd* files
(will usually require superuser to run this command).

## Configuration

There is almost no need to control the program. There is just `global_config.ini`
file which you may adjust according to your railway layout. It is designed to
be configured only once during installation. To further edits are required.

**global_config.ini** is used for basic configuration of device. (e.g.
attribute `[server]` describes the name of server, which application will try to
establish the communication with).

```
[server]
name=server H0
[area]
name=Ku
[logging]
verbosity=debug  # (debug, info, error, critical)
path=  # path to log file, logs to stdout if empty
```

## Soundset configuration

Each sound set contains `config.ini` file:

**config.ini** is used for changing the style of announcements. You can set
either `yes` or `no` to attributes in announcement to be pronounced.

```
[Veronika]  # Name of the sound set, must match directory name
base=Ivona  # Parent sound set, if some files from main sound set are missing,
            # it is completed with the one from the base sound set.
            # This rule applies recursively.
[sound]
gong=yes
salutation=no
trainNum=yes
time=no
```

## Contributors

This application was developed by Petr Repa as a bachelor thesis at Mendel
University in Brno.

## Testing

If you'd like to test the app and you don't have an access to hJOPserver, you
can try to run `network_services_server.py` which works as hJOPserver emulator.
Just run it using Python 3.* in second window of terminal.

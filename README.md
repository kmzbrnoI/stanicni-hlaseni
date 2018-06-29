# Station Announcements
Station announcements is client-based application. It is based on commands from hJOPserver. It is a simulation of station announcements that you know from the train stations.

## Before You Start

### Sound Sets ## 
You need to assign sound files, before you start the program. The sound sets are available [here](https://github.com/kmzbrnoI/shZvuky). 
shZvuky repository uses git-lfs. To install git-lfs on RPI use **instal_lfs.sh** in stanicni-hlaseni directory.

### WiFi ###
RPI 3 uses wpa_supplicant. You can use example wpa_supplicant.conf file in stanicni-hlaseni directory. Just change the password and use cp stanicni-hlaseni/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf to rewrite the default file.

## How to Use It
There is almost no need to control the program. There are just two configuration files in which you can change the application behavior. 

**config.ini** is used for change the style of announcements. You can set either yes or no to attributes in announcement to be pronounced. It's located in each sound set directory.

```
[Veronika] -- Main sound set
base=Ivona -- Parent sound set, if some file from main sound set is missing, it is completed with the one from the base sound set.
[sound] -- used for remove the parts from announcement.
gong=yes
salutation=no
trainNum=yes
time=no
```

**global_config.ini** is used for basic configuration of device. (e.g. attribute [server] describes the name of server, which will application try to establish the communication)
```
[server] 
name=server H0
[area]
name=Ku
[logging]
verbosity=debug -- the level of logging
path= -- it will log to file in stanicni-hlaseni directory
```

## Installation

To install the station announcements as a *systemd* service, simple run
`make install`. Service will be run in current directory, so do not remove
repository!

To uninstall a service, run `make uninstall`.

*Note*: `make install` and `make uninstall` require access to *systemd* files
(will usually require superuser to run this command).

## Read-only FS
This application was tested to run in RO mode with Raspbian Stretch Lite. Probably the easiest way to make the Raspbian run in read-only mode is to use this [script](https://github.com/ways/rpi-readonly).


## Contributors
Developed by Petr Repa as bachelor thesis.

## Development
This application is developed especially for Raspberry Pi 3 with Raspbian OS.

## Testing
If you'd like to test the app and you don't have an access to hJOPserver, you can try to run NetworkServiceClient.py which works as hJOPserver emulator. Just run it using Python 3.* in second window of terminal.

#!/bin/bash  

#ln wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf 
#wpa_supplicant -iwlan0 -cwpa_supplicant.conf 

dhclient -r
#shutdown wpa_supplicant
killall wpa_supplicant
#down interface
ifdown --force wlan0
sleep 1

sudo wpa_supplicant -cwpa_supplicant.conf -B -Dwext -iwlan0 

sudo systemctl daemon-reload
sudo systemctl restart dhcpcd

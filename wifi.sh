#!/bin/bash  

sudo dhclient -r
sudo shutdown wpa_supplicant
sudo killall wpa_supplicant
sudo ifdown --force wlan0
sudo sleep 1

sudo wpa_supplicant -cwpa_supplicant.conf -B -Dwext -iwlan0 

#sudo systemctl daemon-reload
sudo systemctl restart dhcpcd

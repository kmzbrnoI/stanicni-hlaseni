#!/bin/bash

server_ip=$1
home_folder=$2
echo "ls" | smbclient //$server_ip/$home_folder -N -c | grep "   D   " | awk '{print $1}'

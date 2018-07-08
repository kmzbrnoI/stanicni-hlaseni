#!/bin/bash

server_ip=$1
home_folder=$2
sound_set=$3
smbclient //$server_ip/$home_folder -N -c "prompt;recurse;mget $sound_set"

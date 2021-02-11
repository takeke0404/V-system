#!/bin/bash

if [ $# -ge 1 ]  ; then
    cd ~/rasp/
    /usr/local/bin/python3.9 ./v_cron.py $1
else
    echo "Error: argument"
    exit 1
fi

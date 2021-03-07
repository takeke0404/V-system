#!/bin/bash

cd ~/rasp3/
/usr/local/bin/python3.9 ./v_cron2.py >> /home/hk/rasp3/log/v_cron2.log 2>> /home/hk/rasp3/log/v_cron2_error.log

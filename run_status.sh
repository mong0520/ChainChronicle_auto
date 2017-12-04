#!/bin/bash

CONFIG=$1
while true
do
	./cc_main.py -c $CONFIG -a status -n 999999
    sleep 3
done

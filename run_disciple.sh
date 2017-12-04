#!/bin/bash

CONFIG=$1
while true
do
	./cc_main.py -c $CONFIG
    sleep 3
done

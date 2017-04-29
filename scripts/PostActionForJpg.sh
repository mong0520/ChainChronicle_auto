#!/bin/bash
# This script should be run after decode scr files in Windows
rm -f resource/*.scr
mv resource/*.jpg ../img/
python resize_image.py ../img/
cd ../
zip -9 cc_image.zip img/*

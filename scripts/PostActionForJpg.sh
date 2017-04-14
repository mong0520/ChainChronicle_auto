#!/bin/bash
# This script should be run after decode scr files in Windows
rm -f resource/*.scr
mv resource/*.jpg ../jpg/
python resize_image.py ../jpg/
cd ../
zip -9 cc_image.zip img/*

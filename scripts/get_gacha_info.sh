#!/bin/bash

rm -f result.txt
rm -f temp.html
python3 gacha_info.py 1 > temp.html
cat temp.html  | grep execGacha

python3 gacha_info.py 2 > temp.html
cat temp.html  | grep execGacha

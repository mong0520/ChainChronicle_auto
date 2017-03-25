#!/bin/bash

rm -f result.txt
rm -f temp.html
python gacha_info.py > temp.html
cat temp.html | grep 'event_id' > result.txt
cat temp.html | grep -A 5 'var map_event_gacha_type' >> result.txt
cat result.txt

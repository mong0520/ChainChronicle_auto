#!/bin/bash

cd ../
python cc_account_emulator_simple2.py -f uuid-1.txt -t 200 > /tmp/uuid-1.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid-2.txt -t 200 > /tmp/uuid-2.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid-3.txt -t 200 > /tmp/uuid-3.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid-4.txt -t 200 > /tmp/uuid-4.log  2>&1 &

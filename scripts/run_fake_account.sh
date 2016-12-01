#!/bin/bash

cd ../
python cc_account_emulator_simple2.py -f uuid_android2.txt -t 200 > /tmp/uuid_android2.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid_ios.txt -t 200 > /tmp/uuid_ios.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid_android.txt -t 200 > /tmp/uuid_android.log  2>&1 &
python cc_account_emulator_simple2.py -f uuid_ios2.txt -t 200  > /tmp/uuid_ios2.log  2>&1 &

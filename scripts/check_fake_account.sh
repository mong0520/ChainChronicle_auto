#!/bin/bash

count="$(ps -ef | grep cc_account_emulator_simple2 | wc -l)"
echo $count
if [ $count != 5 ]; then
  echo "something wrong, kill all, then re-run"
  ps -ef | grep cc_account_emulator_simple2 | awk '{print $2 }' | xargs kill 9
  ./run_fake_account.sh
else
  echo "running well"
fi

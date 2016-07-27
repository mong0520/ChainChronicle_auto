#!/bin/bash

mkdir resource
python get_latest_card_id.py $1
tar zcvf cc_card.tgz resource/*
rm -rf resource/*

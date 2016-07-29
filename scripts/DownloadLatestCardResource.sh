#!/bin/bash

mkdir resource
python DownloadLatestCardResource.py $1
tar zcvf cc_card.tgz resource/*
rm -rf resource/*

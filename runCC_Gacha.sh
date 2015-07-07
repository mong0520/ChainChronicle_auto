#! /bin/bash
for ((i=1;i<=10;i=i+1))
do
	python cc.py -type gacha -count 200 -sell 1
done

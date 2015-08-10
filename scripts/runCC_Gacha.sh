#! /bin/bash
for ((i=1;i<=200;i=i+1))
do
	python cc.py setting.ini -action gacha
done

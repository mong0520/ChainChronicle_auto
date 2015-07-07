#! /bin/bash

cd /home/ubuntu/ChainChronicle/

# Needs 20000/81 = 247 Stamina fruits
python cc.py -type quest -qid 220512 -count 20000 -raid 1

# total 4,000 cards
for ((i=1;i<=20;i=i+1))  
do
        python cc.py -type gacha -count 200 -sell 1
done

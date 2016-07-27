# -*- coding: utf-8 -*
import sys
sys.path.append("../")
import utils.poster
import simplejson as json
import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.cc

data_mapping = {
    'charainfo': db.charainfo,
    'questdigest': db.questdigest
}

# Get latest charainfo data
for data in data_mapping.keys():
    url = 'http://v252.cc.mobimon.com.tw/data/' + data
    r = utils.poster.Poster.post_data(url)
    # print r[data]
    
    # Remove old data
    data_mapping[data].remove({})

    # Insert latest data
    for element in r[data]:
        # ad-hoc for quest info
        if type(element) is list:
            for doc in element:
                collection = data_mapping[data].insert_one(doc)
        elif type(element) is dict:
            collection = data_mapping[data].insert_one(element)




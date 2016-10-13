# -*- coding: utf-8 -*
import sys
from tinydb import TinyDB, where, Query
import simplejson as json
import os
sys.path.append("../")
import utils.poster


CHARAINFO_DB = 'charainfo.db'
QUESTDIGEST_DB = 'questdigest.db'

if os.path.exists(CHARAINFO_DB):
    os.unlink(CHARAINFO_DB)
if os.path.exists(QUESTDIGEST_DB):
    os.unlink(QUESTDIGEST_DB)

data_mapping = {
    'charainfo': {
        'db_obj': TinyDB(CHARAINFO_DB),
        'raw_list': list()
    },
    'questdigest':{
        'db_obj': TinyDB(QUESTDIGEST_DB),
        'raw_list': list()
    }
}

charainfo_dict = dict()
# Get latest charainfo data
for data in data_mapping.keys():
    data_mapping[data]['db_obj'].purge()
    url = 'http://v267b.cc.mobimon.com.tw/data/' + data
    r = utils.poster.Poster.post_data(url)
    # print json.dumps(r, ensure_ascii=False)

    # Insert latest data
    charainfo_list = list()
    for element in r[data]:
        # ad-hoc for quest info
        if type(element) is list:
            for doc in element:
                data_mapping[data]['raw_list'].append(data)
        elif type(element) is dict:
            data_mapping[data]['raw_list'].append(element)
    data_mapping[data]['db_obj'].insert_multiple(data_mapping[data]['raw_list'])
    data_mapping[data]['db_obj'].close()





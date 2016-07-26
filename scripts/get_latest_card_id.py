import requests
import time
import simplejson as json
import re

date = '20160721_252'
timestamp = int(time.time() * 1000) 
cnt = format(timestamp + 5000, 'x')

pattern = "cha_2d_card_(\d+)\.bdl"

r = requests.get('http://content.cc.mobimon.com.tw/game/{0}/Bdl45_And/files.json?cnt={1}&timestamp={2}'.format(date, cnt, timestamp))
raw_data = json.loads(r.text)

card_id_list = raw_data['files']['Card_OrgSize'].keys()
result = list()
for card_id in card_id_list:
    m = re.search(pattern, card_id)
    try:
        tmp_idx = m.group(1).zfill(5)
        result.append(tmp_idx)
    except:
        pass
result.sort()

for r in result:
    print r
#print json.dumps(card_id_list, indent=2, sort_keys=True)

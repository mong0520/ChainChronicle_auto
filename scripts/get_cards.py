#!/usr/bin/env python3
import requests
import time
import simplejson as json
import re
import sys
import os
sys.path.append('../')
from lib import session_client
from utils import awget
import urllib.request, urllib.parse, urllib.error
import asyncio

start_time = time.time()
timestamp = int(time.time() * 1000)
cnt = format(timestamp + 5000, 'x')
pattern = "cha_2d_card_(\d+)\.bdl"
output_path = '../resource'

if not os.path.exists(output_path):
    os.makedirs(output_path)

def get_content_url():
    ret = session_client.login('ANDO822adb47-dd36-41ce-8640-9f17604d0778')
    #print(json.dumps(ret))
    try:
        return ret['ctroot']
    except:
        return None
        #print(json.dumps(ret, ensure_ascii=False).encode('utf-8'))


ctroot = get_content_url()
#print(ctroot)

request_url = '{0}Bdl54_And/files.json?cnt={1}&timestamp={2}'.format(ctroot, cnt, timestamp)
#print(request_url)
r = requests.get(request_url)
try:
    raw_data = json.loads(r.text)
except:
    print("Unable to get response data, exit")
    sys.exit(0)

card_id_list = list(raw_data['files']['Card_OrgSize'].keys())
result = list()
for card_id in card_id_list:
    m = re.search(pattern, card_id)
    try:
        tmp_idx = m.group(1).zfill(5)
        # skip non-character cards
        if int(tmp_idx) >= 85001:
            continue
        # weapons
        if int(tmp_idx) >= 26000 and int(tmp_idx) <=26127:
            continue
        file_name = 'cha_2d_card_{0}.scr'.format(tmp_idx)
        url = '{0}Resource/Card/{1}'.format(ctroot, file_name)
        result.append(url)
    except:
        pass
result.sort()

# Get file in async mode
loop = asyncio.get_event_loop()
loop.run_until_complete(awget.run(result, output_path=output_path))
print(time.time() - start_time)

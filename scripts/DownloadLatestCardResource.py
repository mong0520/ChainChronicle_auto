import requests
import time
import simplejson as json
import re
import sys
from Queue import Queue
from threading import Thread
import wget
import os
sys.path.append('../')
from lib import session_client
from utils import poster
import urllib

q = Queue(maxsize=0)
num_threads = 10
timestamp = int(time.time() * 1000)
cnt = format(timestamp + 5000, 'x')
pattern = "cha_2d_card_(\d+)\.bdl"
output_path = 'resource'
downloaded_file_list = 'processedCardList.txt'

def do_stuff(q):
    while True:
        url = q.get()
        print url
        if url:
            filename = wget.download(url, out=output_path)
            file_size = os.stat(filename).st_size
            if file_size and file_size < 5000:
                os.remove(filename)
            q.task_done()

def get_content_url():
    ret = session_client.login('ANDO822adb47-dd36-41ce-8640-9f17604d0778')

    try:
        return ret['ctroot']
    except:
        return None
        print json.dumps(ret, ensure_ascii=False).encode('utf-8')


ctroot = get_content_url()
print ctroot

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()

#request_url = 'http://content.cc.mobimon.com.tw/CC/game09/{0}/Bdl45_And/files.json?cnt={1}&timestamp={2}'.format(date, cnt, timestamp)
request_url = '{0}Bdl52_iOS/files.json?cnt={1}&timestamp={2}'.format(ctroot, cnt, timestamp)
print request_url
r = requests.get(request_url)

try:
    raw_data = json.loads(r.text)
except:
    print "Unable to get response data, exit"
    sys.exit(0)

card_id_list = raw_data['files']['Card_OrgSize'].keys()
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
        result.append(tmp_idx)
    except:
        pass
result.sort()

try:
    with open (downloaded_file_list, 'r') as f_in:
        processed_card_list = [line.rstrip() for line in f_in]
except:
    processed_card_list = list()


# print processed_card_list
with open (downloaded_file_list, 'a') as f:
    f.writelines(["%s\n" % item  for item in result])
    for r in result:
        url = '{0}Resource/Card/cha_2d_card_{1}.scr'.format(ctroot, r)
        if r not in processed_card_list:
            print 'Put #{0} in downloading queue'.format(r)
            q.put(url)
            f.write('{0}\n'.format(r))

q.join()


# Remove incorrect files


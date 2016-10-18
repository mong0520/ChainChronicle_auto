import requests
import time
import simplejson as json
import re
import sys
from Queue import Queue
from threading import Thread
import wget
import os

q = Queue(maxsize=0)
num_threads = 10
timestamp = int(time.time() * 1000)
cnt = format(timestamp + 5000, 'x')
pattern = "cha_2d_card_(\d+)\.bdl"
output_path = 'resource'


def do_stuff(q):
    while True:
        url = q.get()
        if url:
            filename = wget.download(url, out=output_path)
            file_size = os.stat(filename).st_size
            if file_size and file_size < 5000:
                os.remove(filename)
            q.task_done()

try:
    date = sys.argv[1]
except IndexError as e:
    print "Please speicfy date argument, for example '20161013_522'"
    sys.exit(0)

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()

#request_url = 'http://content.cc.mobimon.com.tw/CC/game09/{0}/Bdl45_And/files.json?cnt={1}&timestamp={2}'.format(date, cnt, timestamp)
request_url = 'http://content.cc.mobimon.com.tw/CC/267/{0}/Bdl52_And/files.json?cnt={1}&timestamp={2}'.format(date, cnt, timestamp)
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
        result.append(tmp_idx)
    except:
        pass
result.sort()

for r in result:
    url = 'http://content.cc.mobimon.com.tw/CC/267/{0}/Resource/Card/cha_2d_card_{1}.scr'.format(date, r)
    q.put(url)

q.join()


# Remove incorrect files


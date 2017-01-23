import utils.poster
import time
import urllib
import requests
import sys
sys.path.append('utils')
from poster import Poster
import zlib
import json

def compose(sid, ba, mt_list):
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/card/compose'
    headers = {'Cookie': 'sid={0}'.format(sid)}
    headers.update(Poster.DEFAULT_HEADERS)
    cookies = {'sid': sid}
    # data = {
    #     'ba': ba,
    #     'expup_id' : 0,
    #     'mt': mt_list
    # }
    data = dict()
    data['timestamp'] = int(time.time() * 1000)
    data['cnt'] = format(data['timestamp'] + 5000, 'x')
    query_string = '?ba={0}&mt='.format(ba) + '&mt='.join(mt_list) + '&expup_id=0&cnt={0}&timestamp={1}'.format(
        data['cnt'], data['timestamp'])
    # print query_string

    post_url = url + query_string
    # print post_url
    payload = urllib.quote_plus(query_string)
    payload = 'nature=' + payload
    # print payload

    r = requests.post(post_url, data=payload, headers=headers, cookies=cookies)
    # print r.content
    # return None
    decompressed_data = zlib.decompress(r.content, 16+zlib.MAX_WBITS)
    return json.loads(decompressed_data)


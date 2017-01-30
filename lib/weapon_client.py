import utils.poster
import time
import urllib
import requests
import sys
sys.path.append('utils')
from poster import Poster
import zlib
import json


def compose(sid, weapon_list):
    """ Due to this api use same key 'mt' 5 times, so it can not use commom poster lib"""
    url = "http://v272.cc.mobimon.com.tw/weapon/compose"
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    headers.update(Poster.DEFAULT_HEADERS)
    cookies = {'sid': sid}

    data['timestamp'] = int(time.time() * 1000)
    data['cnt'] = format(data['timestamp'] + 5000, 'x')
    # query_string = urllib.urlencode(data)
    query_string = "?mt={0}&mt={1}&mt={2}&mt={3}&mt={4}&timestamp={5}&cnt={6}".format(
        weapon_list[0], weapon_list[1], weapon_list[2], weapon_list[3], weapon_list[4], data['timestamp'], data['cnt'])
    # query_string += "&eid=3" #  special event
    post_url = url + query_string
    # print post_url
    payload = urllib.quote_plus(query_string)
    payload = 'nature=' + payload
    # print payload

    r = requests.post(post_url, data=payload, headers=headers, cookies=cookies)
    decompressed_data = zlib.decompress(r.content, 16+zlib.MAX_WBITS)
    # print decompressed_data
    return json.loads(decompressed_data)




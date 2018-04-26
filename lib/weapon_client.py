import utils.poster
import time
import urllib.request, urllib.parse, urllib.error
import requests
import sys
sys.path.append('utils')
from poster import Poster
import zlib
import json
import utils.global_config


def compose(sid, weapon_list, eid=None):
    """ Due to this api use same key 'mt' 5 times, so it can not use commom poster lib"""
    url = "{0}/weapon/compose".format(utils.global_config.get_hostname())
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    headers.update(Poster.DEFAULT_HEADERS)
    cookies = {'sid': sid}

    data['timestamp'] = int(time.time() * 1000)
    data['cnt'] = format(data['timestamp'] + 5000, 'x')
    # query_string = urllib.urlencode(data)
    query_string = "?wia={0}&wia={1}&wia={2}&wia={3}&wia={4}&timestamp={5}&cnt={6}".format(
        weapon_list[0], weapon_list[1], weapon_list[2], weapon_list[3], weapon_list[4], data['timestamp'], data['cnt'])
    if eid:
        query_string += "&eid={0}".format(eid) #  special event
    post_url = url + query_string
    print(post_url)
    payload = urllib.parse.quote_plus(query_string)
    payload = 'nature=' + payload
    print(payload)

    r = requests.post(post_url, data=payload, headers=headers, cookies=cookies)
    decompressed_data = zlib.decompress(r.content, 16+zlib.MAX_WBITS)
    # print(decompressed_data)
    return json.loads(decompressed_data)




import requests
import time
import urllib.request, urllib.parse, urllib.error
import zlib
import json
import utils.global_config as global_config

class Poster(object):

    VERBOSE = False

    DEFAULT_HEADERS = {
        'X-Unity-Version': '5.4.4f1',
        'Device': '0',
        'Platform': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'AppVersion': '3.22',
        'user-agent': 'Chronicle/3.2.2 Rev/2014 (iPhone OS 10.2) DeviceWidth:1024',
        'Accept-Encoding': 'identity',
        'Host': '{0}'.format(global_config.get_fqdn()),
        'Connection': 'Keep-Alive'
    }

    def __init__(self):
        pass


    @staticmethod
    def post_data_general(sid, path, **kwargs):
        url = "{0}{1}".format(global_config.get_hostname(), path)

        data = dict()
        if kwargs:
            for k, v in kwargs.items():
                data[k] = v
        headers = {'Cookie': 'sid={0}'.format(sid)}
        cookies = {'sid': sid}
        ret = Poster.post_data(url, headers, cookies, **data)
        return ret


    @staticmethod
    def __post_data(url, headers=dict(), cookies=None, payload=None, **kwargs):
        # kwargs['timestamp'] = int(time.time())
        kwargs['timestamp'] = int(time.time() * 1000)
        kwargs['cnt'] = format(kwargs['timestamp'] + 5000, 'x')
        query_string = urllib.parse.urlencode(kwargs)
        post_url = '?'.join([url, query_string])
        kwargs.pop('timestamp', None)
        if payload is None:
            payload = urllib.parse.quote_plus(urllib.parse.urlencode(kwargs))
            payload = 'nature=' + payload

        if global_config.is_debug():
            print(post_url)
        # print(post_url)
        # print payload
        headers.update(Poster.DEFAULT_HEADERS)
        # print headers
        r = requests.post(post_url, data=payload, headers=headers, cookies=cookies)
        # print "encoding = {0}".format(r.headers)
        # r.headers['Content-Type'] = ''
        # r.headers['content-encoding'] = 'gzip'
        # r.headers['Content-Type'] = 'application/x-gzip'
        # print "encoding = {0}".format(r.headers)
        # print r.text

        # gzip decompress in-the-fly
        decompressed_data = zlib.decompress(r.content, 16+zlib.MAX_WBITS)
        if global_config.is_debug():
            print(decompressed_data)
        return decompressed_data


        # chunk_size = 1
        # with open('login.gz', 'wb') as fd:
        #     for chunk in r.iter_content(chunk_size):
        #         fd.write(chunk)
        # return r

    @staticmethod
    def post_data(url, headers=dict(), cookies=None, payload=None, **kwargs):
        json_data = Poster.__post_data(url, headers, cookies, payload, **kwargs).decode('utf-8')
        return json.loads(json_data)

    @staticmethod
    def post_data_v2(url, headers=dict(), cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs)

    @staticmethod
    def get_data(url):
        # return requests.get(url, headers=Poster.DEFAULT_HEADERS).json()
        r = requests.get(url, headers=Poster.DEFAULT_HEADERS)
        decompressed_data = zlib.decompress(r.content, 16+zlib.MAX_WBITS).decode('utf-8')
        return json.loads(decompressed_data)

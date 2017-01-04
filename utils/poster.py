import requests
import time
import urllib
import zlib
import json

class Poster(object):

    DEFAULT_HEADERS = {
        'X-Unity-Version': '5.4.0f3',
        'Device': '0',
        'Platform': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'AppVersion': '2.72',
        'user-agent': 'Chronicle/2.7.2 Rev/45834 (Android OS 6.0.1 / API-23)',
        'Accept-Encoding': 'identity',
        'Host': 'v272.cc.mobimon.com.tw',
        'Connection': 'Keep-Alive'
    }

    def __init__(self):
        pass

    @staticmethod
    def __post_data(url, headers=None, cookies=None, payload=None, **kwargs):
        # kwargs['timestamp'] = int(time.time())
        kwargs['timestamp'] = int(time.time() * 1000)
        kwargs['cnt'] = format(kwargs['timestamp'] + 5000, 'x')
        query_string = urllib.urlencode(kwargs)
        post_url = '?'.join([url, query_string])
        kwargs.pop('timestamp', None)
        if payload is None:
            payload = urllib.quote_plus(urllib.urlencode(kwargs))
            payload = 'nature=' + payload

        # print post_url
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
        return decompressed_data


        # chunk_size = 1
        # with open('login.gz', 'wb') as fd:
        #     for chunk in r.iter_content(chunk_size):
        #         fd.write(chunk)
        # return r

    @staticmethod
    def post_data(url, headers=None, cookies=None, payload=None, **kwargs):
        return json.loads(Poster.__post_data(url, headers, cookies, payload, **kwargs))

    @staticmethod
    def post_data_v2(url, headers=None, cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs)

    @staticmethod
    def get_data(url):
        # return requests.get(url, headers=Poster.DEFAULT_HEADERS).json()
        return json.loads(requests.get(url, headers=Poster.DEFAULT_HEADERS))

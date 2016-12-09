import requests
import time
import urllib

class Poster(object):

    DEFAULT_HEADERS = {
        'X-Unity-Version': '5.4.0f3',
        'Device': '0',
        'Platform': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'AppVersion': '2.67',
        'user-agent': 'Chronicle/2.6.7 Rev/45834 (Android OS 6.0.1 / API-23',
        'Accept-Encoding': 'identity',
        'Host': 'v267.cc.mobimon.com.tw',
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
        # print r.text
        return r

    @staticmethod
    def post_data(url, headers=None, cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs).json()

    @staticmethod
    def post_data_v2(url, headers=None, cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs)

    @staticmethod
    def get_data(url):
        return requests.get(url, headers=Poster.DEFAULT_HEADERS).json()

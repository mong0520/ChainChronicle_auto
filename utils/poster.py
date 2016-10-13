import requests
import time
import urllib


class Poster(object):

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
        r = requests.post(post_url, data=payload, headers=headers, cookies=cookies)
        return r

    @staticmethod
    def post_data(url, headers=None, cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs).json()

    @staticmethod
    def post_data_v2(url, headers=None, cookies=None, payload=None, **kwargs):
        return Poster.__post_data(url, headers, cookies, payload, **kwargs)

import requests
import time
import urllib

class Poster(object):

    def __init__(self):
        self.headers = dict()
        self.cookies = dict()

    def post_data(self, url, headers=None, cookies=None, **kwargs):
        kwargs['cnt'] = int(time.time() * 1000)
        kwargs['timestamp'] = format(kwargs['cnt'] + 5000, 'x')
        query_string = urllib.urlencode(kwargs)
        payload = "nature=cnt%3d{0}%26t%3d6".format(kwargs['cnt'])
        post_url = '?'.join([url, query_string])
        # print post_url
        # print payload.lower()
        r = requests.post(post_url, data=payload, headers=headers, cookies=cookies).json()
        return r

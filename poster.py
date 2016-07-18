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
        post_url = '?'.join([url, query_string])

        kwargs.pop('timestamp', None)
        payload = urllib.quote_plus(urllib.urlencode(kwargs))
        payload = 'nature=' + payload
        #print payload
        # print post_url
        # print payload.lower()
        r = requests.post(post_url, data=payload, headers=headers, cookies=cookies).json()
        return r


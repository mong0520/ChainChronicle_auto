import requests
import time
import urllib

class Poster(object):

    def __init__(self):
        self.headers = dict()
        self.cookies = dict()
        # self.headers = {
        #     'X-Unity-Version': '4.6.5f1',
        #     'Device': '0',
        #     'AppVersion': '2.22',
        #     'Accept-Encoding': 'identity',
        #     'user-agent': 'Chronicle/2.2.2 Rev/20320 (Android OS 4.4.4 / API-19 (KTU84P/V6.5.3.0.KXDMICD))',
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'Platform': '2',
        #     'Host': 'prod4.cc.mobimon.com.tw',
        #     'Connection': 'Keep-Alive',
        #     'Content-Length': '1506'
        # }

    # def set_header(self, header_dict):
    #     self.headers = header_dict
    #
    # def set_cookies(self, cookies):
    #     self.cookies = cookies

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

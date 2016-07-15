import requests
import time
import urllib

class Poster(object):

    def __init__(self):
        self.sid = None
        self.headers = {
            'X-Unity-Version': '4.6.5f1',
            'Device': '0',
            'AppVersion': '2.22',
            'Accept-Encoding': 'identity',
            'user-agent': 'Chronicle/2.2.2 Rev/20320 (Android OS 4.4.4 / API-19 (KTU84P/V6.5.3.0.KXDMICD))',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Platform': '2',
            'Host': 'prod4.cc.mobimon.com.tw',
            'Connection': 'Keep-Alive',
            'Content-Length': '1506'
        }

    def set_sid(self, sid):
        self.sid = sid

    def post_data(self, url, **kwargs):
        # now = int(time.time() * 1000)
        # hex_now = format(now + 5000, 'x')
        kwargs['cnt'] = int(time.time() * 1000)
        kwargs['timestamp'] = format(kwargs['cnt'] + 5000, 'x')
        query_string = urllib.urlencode(kwargs)
        payload = "nature=cnt%3d{0}%26t%3d6".format(kwargs['cnt'])
        post_url = url + query_string
        print post_url
        print payload.lower()
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
        }
        cookies = {'sid': self.sid}
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        print r
        # return r
        # for k, v in kwargs.items():
        #     query_string_list.append("{0}={1}".format(k, v))
        # query_string = '&'.join(query_string_list)
        # print query_string

        #
        # for k, v in kwargs.items():
        #     print 'Optional argument %s (*kwargs): %s' % (k, v)
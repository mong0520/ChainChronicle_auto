import utils.poster
import time


def get_alldata(sid):
    poster = utils.poster.Poster
    #url = "http://ios5.cc.mobimon.com.tw/user/all_data"
    url = "http://v267.cc.mobimon.com.tw/user/all_data"
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret


import utils.poster
import utils.global_config
import time


def get_alldata(sid):
    poster = utils.poster.Poster
    #url = "http://ios5.cc.mobimon.com.tw/user/all_data"
    url = "{0}/user/all_data".format(utils.global_config.get_hostname())
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret


def get_allcards(sid):
    r = get_alldata(sid)
    return r['body'][6]['data']

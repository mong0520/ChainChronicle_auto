import utils.poster
import time
import utils.global_config

def tutorial(sid, entry=False, **kwargs):
    poster = utils.poster.Poster
    #url = "http://ios5.cc.mobimon.com.tw/user/all_data"
    url = "{0}/tutorial".format(utils.global_config.get_hostname())
    if entry:
        url += '/entry'
    data = dict()
    for k, v in kwargs.items():
        data[k] = v
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret


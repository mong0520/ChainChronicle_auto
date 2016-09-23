import utils.poster


def get_account(sid):
    poster = utils.poster.Poster
    url = "http://v267.cc.mobimon.com.tw/user/get_account"
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret


def set_password(password, sid):
    poster = utils.poster.Poster
    url = "http://v267.cc.mobimon.com.tw/user/set_password"
    data = {'pass': password}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

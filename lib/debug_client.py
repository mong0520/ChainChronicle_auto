import utils.poster


def debug_poc(sid, path, **kwargs):
    poster = utils.poster.Poster
    url = "http://v272.cc.mobimon.com.tw{0}".format(path)

    data = dict()
    for k, v in kwargs.iteritems():
        data[k] = v
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

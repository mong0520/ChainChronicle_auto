import utils.poster


def debug_post(sid, path, **kwargs):
    poster = utils.poster.Poster
    # url = "http://v272.cc.mobimon.com.tw{0}".format(path)
    # data = dict()
    # for k, v in kwargs.iteritems():
        # data[k] = v
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data_general(sid, path, **kwargs)
    return ret

import utils.poster
import utils.global_config


def debug_post(sid, path, **kwargs):
    poster = utils.poster.Poster
    # url = "{0}{1}".format(utils.globa_config.gethostname(), path)
    # data = dict()
    # for k, v in kwargs.iteritems():
        # data[k] = v
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data_general(sid, path, **kwargs)
    return ret

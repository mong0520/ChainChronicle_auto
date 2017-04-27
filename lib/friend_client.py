import utils.poster
import utils.global_config


def query_fid(sid, oid):
    poster = utils.poster.Poster
    url = "{0}/friend/search".format(utils.global_config.get_hostname())
    data = {'oid': oid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

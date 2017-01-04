import utils.poster


def query_fid(sid, oid):
    poster = utils.poster.Poster
    url = "http://v272.cc.mobimon.com.tw/friend/search"
    data = {'oid': oid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

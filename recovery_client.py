import utils.poster
import time


def recovery_ap(parammeter, sid):
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/user/recover_ap'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'type': parammeter['type'],
        'item_id': parammeter['item_id']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


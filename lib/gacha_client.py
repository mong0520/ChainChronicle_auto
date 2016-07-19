import utils.poster
import time


def gacha(parammeter, sid):
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/gacha'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    if parammeter['type'] == 3:  # Raid Gacha
        parammeter['batch_count'] = 10
        sleep_time = 5
    else:
        parammeter['batch_count'] = 1
        sleep_time = 0
    data = {
        't': parammeter['type'],
        'c': parammeter['batch_count']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    time.sleep(sleep_time)
    return r


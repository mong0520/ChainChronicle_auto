import utils.poster
import time


def gacha(parammeter, sid):
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/gacha'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    # if parammeter['type'] in [3, 8]:  # Raid Gacha and Sugjugation Gacha
        # parammeter['batch_count'] = 10
        #sleep_time = 5
        # sleep_time = 1
    # else:
    # parammeter['batch_count'] = 1
    sleep_time = 0
    data = {
        't': parammeter['type'],
        'c': parammeter['count']
    }
    if 'area' in parammeter and parammeter['area']:
        data['area'] = parammeter['area']
    if 'place' in parammeter and parammeter['place']:
        data['place'] = parammeter['place']
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    time.sleep(sleep_time)
    return r


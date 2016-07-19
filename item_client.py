import utils.poster


def buy_item(parammeter, sid):
    poster = utils.poster.Poster
    url = 'http://v252.cc.mobimon.com.tw/token'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'kind': parammeter['kind'],
        'type': parammeter['type'],
        'id': parammeter['id'],
        'val': parammeter['val'],
        'price': parammeter['price'],
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


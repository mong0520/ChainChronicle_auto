import utils.poster


def get_present_list(sid, card_type=None):
    # Get present list
    poster = utils.poster.Poster
    url = 'http://v267b.cc.mobimon.com.tw/present/list'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {}
    ret = poster.post_data(url, headers, cookies, **data)
    if card_type:
        present_ids = [data['idx'] for data in ret['body'][0]['data'] if data['data']['type'] == card_type]
    else:
        present_ids = [data['idx'] for data in ret['body'][0]['data']]
    # logger.debug("Present ids = {0}".format(present_ids))
    return present_ids


def receieve_present(pid, sid):
    # Get present
    poster = utils.poster.Poster
    url = 'http://v267b.cc.mobimon.com.tw/present/recv'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}

    data = {'p': pid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

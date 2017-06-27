import utils.poster
import utils.global_config


def get_present_list(sid, card_type=None):
    # Get present list
    poster = utils.poster.Poster
    url = '{0}/present/list'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {}
    ret = poster.post_data(url, headers, cookies, **data)
    if card_type:
        present_ids = [data['idx'] for data in ret['body'][0]['data'] if data['data']['type'] == card_type]
    else:
        # present_ids = [data['idx'] for data in ret['body'][0]['data']]
        # work around to get gacha coin
        present_ids = [data['idx'] for data in ret['body'][0]['data'] if data['data']['id'] in [20, ]]
    # logger.debug("Present ids = {0}".format(present_ids))
    return present_ids


def receieve_present(pid, sid):
    # Get present
    poster = utils.poster.Poster
    url = '{0}/present/recv'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}

    data = {'p': pid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

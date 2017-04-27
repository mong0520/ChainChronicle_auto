import utils.poster
import time
import utils.global_config


def recovery_ap(parammeter, sid):
    poster = utils.poster.Poster
    url = '{0}/user/recover_ap'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'type': parammeter['type'],
        'item_id': parammeter['item_id']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


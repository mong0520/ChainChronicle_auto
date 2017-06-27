import utils.poster
import utils.global_config


def get_explorer_information(sid):
    poster = utils.poster.Poster
    url = '{0}/explorer/list'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def start_explorer(parameter, sid):
    poster = utils.poster.Poster
    url = '{0}/explorer/entry'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'explorer_idx': parameter['explorer_idx'],
        'location_id': parameter['location_id'],
        'card_idx': parameter['card_idx'],
        'pickup': parameter['pickup'],
        'interval': parameter['interval'],
        'helper1': '588707',
        'helper2': '1913206'
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r

def cancel_explorer(parameter, sid):
    poster = utils.poster.Poster
    url = '{0}/explorer/cancel'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'explorer_idx': parameter['explorer_idx']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r



def get_explorer_result(idx, sid):
    poster = utils.poster.Poster
    url = '{0}/explorer/result'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'explorer_idx': idx
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def finish_explorer(parameter, sid):
    poster = utils.poster.Poster
    url = '{0}/explorer/finish'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'explorer_idx': parameter['explorer_idx']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r
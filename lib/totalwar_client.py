import utils.poster
import utils.global_config


def accept_totalwar(ring, sid):
    poster = utils.poster.Poster
    url = '{0}/totalwar/accept'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'ring': ring
    }
    r = poster.post_data(url, headers, cookies, **data)
    return r


def start_totalwar(parameter, sid):
    fid = 1683830
    poster = utils.poster.Poster
    url = '{0}/totalwar/entry'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'tid': parameter['tid'],
        'fid': fid,
        'pt': 0
    }
    r = poster.post_data(url, headers, cookies, **data)
    return r


def finish_totalwar(parameter, sid):
    poster = utils.poster.Poster
    url = '{0}/totalwar/result'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'res': 1,
        'tid': parameter['tid']
    }
    r = poster.post_data(url, headers, cookies, **data)
    return r
    # logger.debug(r)

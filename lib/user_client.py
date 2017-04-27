import utils.poster
import utils.global_config


def get_account(sid):
    poster = utils.poster.Poster
    url = "{0}/user/get_account".format(utils.global_config.get_hostname())
    data = {}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    ret = poster.post_data(url, headers, cookies, **data)
    return ret


def set_password(password, sid):
    poster = utils.poster.Poster
    url = "{0}/user/set_password".format(utils.global_config.get_hostname())
    data = {'pass': password}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    cookies = {'sid': sid}
    # self.poster.set_header(headers)
    # self.poster.set_cookies(cookies)
    ret = poster.post_data(url, headers, cookies, **data)
    return ret

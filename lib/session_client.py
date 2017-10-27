import utils.poster
import urllib.request, urllib.parse, urllib.error
import time
import simplejson
import utils.global_config


def login(uid, token=None):
    poster = utils.poster.Poster
    url = '{0}/session/login'.format(utils.global_config.get_hostname())
    headers = {
        'Cookie': 'sid=INVALID'
    }
    data = {
        'UserUniqueID': uid,
        'Token': token,
        'OS': 1
    }
    payload_dict = {
      "APP": {
        "Version": "3.22",
        "Revision": "2014",
        "time": time.time(),
        "Lang": "Chinese"
    },
        "DEV": data
    }
    payload = 'param=' + urllib.parse.quote_plus(simplejson.dumps(payload_dict))
    # print url
    # print payload
    # ret = poster.post_data(url, headers, None, payload, **data)
    ret = poster.post_data(url, headers, None, payload, **data)
    return ret


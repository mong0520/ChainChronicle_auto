# -*- coding: utf-8 -*
import sys
import time
import urllib
import simplejson
sys.path.append('../')
import utils.poster
import lib.friend_client as friend_client

VALID_KEYS = ['uid', 'lv', 'sup_lv', 'name']


def get_sid():
    url = 'http://v267b.cc.mobimon.com.tw/session/login'
    headers = {'Cookie': 'sid=INVALID'}
    data = {
        'UserUniqueID': 'ANDO9c3e5899-4e22-49a5-bf99-82d6b72aec8d',
        'OS': 1
    }
    payload_dict = {
        "APP": {
            "time": time.time()
        },
        "DEV": data
    }
    payload = 'param=' + urllib.quote_plus(simplejson.dumps(payload_dict))
    ret = utils.poster.Poster.post_data(url, headers, None, payload, **data)
    try:
        return ret['login']['sid']
    except KeyError:
        msg = u"無法登入, Message = {0}".format(ret['msg'])
        print msg
        return None


def query_friend(sid, oid):
    return friend_client.query_fid(sid, oid)


def main():
    sid = get_sid()
    result = query_friend(sid, sys.argv[1])
    if 'friend' in result:
        for k, v in result['friend'].iteritems():
            if k in VALID_KEYS:
                print u"{0} = {1}".format(k, v)
    else:
        print 'Query failed'
        print result


if __name__ == '__main__':
    main()


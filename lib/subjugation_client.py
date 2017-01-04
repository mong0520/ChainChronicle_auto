import utils.poster
import time


def check_participant(parameter, sid):
    # Check
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/subjugation/check_participant'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'jid': parameter['jid'],
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def try_subjugation(parameter, sid):
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/subjugation/try'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'brave': 0,
        'jid': parameter['jid'],
        'ecnt': parameter['ecnt']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def start_subjugation(parameter, sid):
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/subjugation/entry'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'bid': parameter['bid'],
        'brave': 0,
        'fid': parameter['fid'],
        'full': 0,
        'jid': parameter['jid'],
        'pt': parameter['pt']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def finish_subjugation(parameter, sid):
    now = int(time.time())
    hex_now = format(now + 5000, 'x')
    poster = utils.poster.Poster
    url = 'http://v272.cc.mobimon.com.tw/subjugation/result'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    pt_cid = parameter['pt_cid']
    fid = parameter['fid']
    data = {
        'res': 1,
        'jid': parameter['jid'],
        'bid': parameter['bid'],
        'wc': parameter['wave'],
        'bt': 6176,
        'cc': 1,
        'time': '0.00',
        'fid': parameter['fid'],
        'd': 1,
        's': 1,

    }
    payload = "mission=%7b%22cid%22%3a%5b{cid0}%2c{cid1}%2c{cid2}%5d%2c%22sid%22%3a%5b0%2c0%2c0%5d%2c%22fid%22%3a{fid}%2c%22ms%22%3a1%2c%22md%22%3a2476%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%2c%225%22%3a0%2c%228%22%3a0%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a2%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a0%2c%22fw%22%3a0%2c%22fo%22%3a0%2c%22cc%22%3a1%2c%22bf_atk%22%3a0%2c%22bf_hp%22%3a0%2c%22bf_spd%22%3a0%7d&nature=bid%3d{bid}%26bt%3d7056%26cc%3d1%26cnt%3d{cnt}%26d%3d1%26jid%3d{jid}%26mission%3d%257b%2522cid%2522%253a%255b{cid0}%252c{cid1}%252c{cid2}%255d%252c%2522sid%2522%253a%255b0%252c0%252c0%255d%252c%2522fid%2522%253a{fid}%252c%2522ms%2522%253a1%252c%2522md%2522%253a2476%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%252c%25225%2522%253a0%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a2%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a0%252c%2522fw%2522%253a0%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%252c%2522bf_atk%2522%253a0%252c%2522bf_hp%2522%253a0%252c%2522bf_spd%2522%253a0%257d%26res%3d1%26s%3d0%26time%3d1.80%26wc%3d{wc}".format(
        cnt=hex_now, now=now, jid=parameter['jid'], bid=parameter['bid'], cid0=pt_cid[0], cid1=pt_cid[1],
        cid2=pt_cid[1], wc=parameter['wave'], fid=fid)
    r = poster.post_data(url, headers, cookies, payload, **data)
    return r

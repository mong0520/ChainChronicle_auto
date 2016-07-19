import utils.poster
import requests
import time


def get_raid_boss_id(sid):
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/raid/list'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    try:
        # bossCount = len(r['body'][0]['data'])
        # logger.debug("Boss Count = {0}".format(bossCount))
        for r in r['body'][0]['data']:
            if r['own']:
                return r['boss_id']
        return None
    except Exception as e:
        return None


def start_raid_quest(parameter, sid):
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/raid/entry'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'bid': parameter['boss_id'],
        'fid': parameter['fid'],
        'pt': 0,
        'use': 1
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def finish_raid_quest(parameter, sid):
    now = int(time.time() * 1000)
    hex_now = format(now + 5000, 'x')
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/quest/result'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'bid': parameter['boss_id'],
        'res': 1,
        'damage': 9994500,
        't': 15
    }
    payload = "mission=%7b%22cid%22%3a%5b1032%2c57%2c7505%2c3022%2c1021%2c38%5d%2c%22fid%22%3a43%2c%22ms%22%3a0%2c%22md%22%3a198601%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a1%2c%22fw%22%3a3%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bid%3d{0}%26cnt%3d{1}%26damage%3d994500%26mission%3d%257b%2522cid%2522%253a%255b1032%252c57%252c7505%252c3022%252c1021%252c38%255d%252c%2522fid%2522%253a43%252c%2522ms%2522%253a0%252c%2522md%2522%253a198601%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%252c%25225%2522%253a1%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a1%252c%2522fw%2522%253a3%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26res%3d1%26t%3d15".format(
        hex_now)
    r = poster.post_data(url, headers, cookies, payload, **data)
    return r


def get_raid_bonus(parameter, sid):
    poster = utils.poster.Poster
    url = 'http://prod4.cc.mobimon.com.tw/raid/record'
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'bid': parameter['boss_id']
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r

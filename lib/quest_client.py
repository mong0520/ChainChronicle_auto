import utils.poster
import time
import requests
import utils.global_config

def get_treasure(quest_info, sid):
    poster = utils.poster.Poster
    url = '{0}/quest/treasure'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'type': quest_info['qtype'],
        'qid': quest_info['qid']
    }
    r = poster.post_data(url, headers, cookies, payload=None,  **data)
    return r

def start_quest(quest_info, sid, version=2):
    # Get Quest
    poster = utils.poster.Poster

    url = '{0}/quest/entry'.format(utils.global_config.get_hostname())
    if version == 3:
        url = '{0}/quest/v3_entry'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        # 'oc': 1,
        'type': quest_info['qtype'],
        'qid': quest_info['qid'],
        'fid': quest_info['fid'],
        'pt': quest_info['pt'],
        'htype': 0
    }
    if 'lv' in quest_info:
        data['lv'] = quest_info['lv']
    if 'hcid' in quest_info:
        data['hcid'] = quest_info['hcid']
    r = poster.post_data(url, headers, cookies, payload=None,  **data)
    return r


def finish_quest(quest_info, sid, version=2):
    cid = [7520]
    now = int(time.time())
    hex_now = format(now + 5000, 'x')
    poster = utils.poster.Poster
    url = '{0}/quest/result'.format(utils.global_config.get_hostname())
    if version == 3:
        url = '{0}/quest/v3_result'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'qid': quest_info['qid'],
        'fid': quest_info['fid'],
        'res': 1,
        'bt': 1200,
        'time': '0.00',
        'd': 1,
        's': 1,
        'cc': 1,
        'wc': 5,
        'wn': 5
    }
    if 'lv' in quest_info:
        data['lv'] = quest_info['lv']

    # payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b7505%2c5033%2c52%2c38%2c7502%2c45%5d%2c%22fid%22%3a{1}%2c%22ms%22%3a1%2c%22md%22%3a200001%2c%22sc%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a0%7d%2c%22es%22%3a1%2c%22at%22%3a1%2c%22he%22%3a1%2c%22da%22%3a1%2c%22ba%22%3a1%2c%22bu%22%3a1%2c%22job%22%3a%7b%220%22%3a1%2c%221%22%3a1%2c%222%22%3a2%2c%223%22%3a1%2c%224%22%3a2%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a2%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a1%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a0%7d%2c%22fj%22%3a-1%2c%22fw%22%3a-1%2c%22fo%22%3a1%2c%22cc%22%3a1%7d&nature=bt%3d1200%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b7505%252c5033%252c52%252c38%252c7502%252c45%255d%252c%2522fid%2522%253a{1}%252c%2522ms%2522%253a0%252c%2522md%2522%253a200000%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a1%252c%25221%2522%253a1%252c%25222%2522%253a2%252c%25223%2522%253a1%252c%25224%2522%253a2%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a1%252c%25224%2522%253a2%252c%25225%2522%253a1%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a-1%252c%2522fw%2522%253a-1%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26qid%3d220103%26res%3d1%26s%3d0%26time%3d0.00%26wc%3d5%26wn%3d5".format(
        # hex_now, quest_info['fid'])
    payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b7520%2c8877%2c8892%2c8170%2c8194%2c7017%5d%2c%22sid%22%3a%5b13003%2c8171%2c8878%2c8158%2c8192%2c11030%5d%2c%22fid%22%3a%5b{1}%5d%2c%22ms%22%3a0%2c%22md%22%3a9280%2c%22sc%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a2%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a2%2c%224%22%3a0%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a1%2c%225%22%3a2%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a1%7d%2c%22box%22%3a2%2c%22um%22%3a%7b%221%22%3a2%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a0%2c%22fw%22%3a0%2c%22fo%22%3a0%2c%22mlv%22%3a80%2c%22mbl%22%3a21%2c%22udj%22%3a0%2c%22sdmg%22%3a89009%2c%22tp%22%3a11%2c%22gma%22%3a8%2c%22gmr%22%3a6%2c%22gmp%22%3a0%2c%22stp%22%3a0%2c%22uh%22%3a%7b%2218%22%3a1%2c%223%22%3a4%2c%2220%22%3a1%2c%221%22%3a1%7d%2c%22cc%22%3a1%2c%22bf_atk%22%3a0%2c%22bf_hp%22%3a0%2c%22bf_spd%22%3a0%7d&bl=%5b%7b%22src_cid%22%3a7520%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a8877%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a8892%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a8170%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a8202%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a7017%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%5d&blf=%5b%7b%22src_cid%22%3a8894%2c%22mana%22%3a20%2c%22use_skill%22%3atrue%7d%5d&nature=bl%3d%255b%257b%2522src_cid%2522%253a7520%252c%2522mana%2522%253a2%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a8877%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a8892%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a8170%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a8202%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a7017%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%255d%26blf%3d%255b%257b%2522src_cid%2522%253a8894%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253atrue%257d%255d%26bt%3d7983%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b7520%252c8877%252c8892%252c8170%252c8194%252c7017%255d%252c%2522sid%2522%253a%255b13003%252c8171%252c8878%252c8158%252c8192%252c11030%255d%252c%2522fid%2522%253a%255b{1}%255d%252c%2522ms%2522%253a0%252c%2522md%2522%253a9280%252c%2522sc%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a2%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a2%252c%25224%2522%253a0%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a1%252c%25225%2522%253a2%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a1%257d%252c%2522box%2522%253a2%252c%2522um%2522%253a%257b%25221%2522%253a2%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a0%252c%2522fw%2522%253a0%252c%2522fo%2522%253a0%252c%2522mlv%2522%253a80%252c%2522mbl%2522%253a21%252c%2522udj%2522%253a0%252c%2522sdmg%2522%253a89009%252c%2522tp%2522%253a11%252c%2522gma%2522%253a8%252c%2522gmr%2522%253a6%252c%2522gmp%2522%253a0%252c%2522stp%2522%253a0%252c%2522uh%2522%253a%257b%252218%2522%253a1%252c%25223%2522%253a4%252c%252220%2522%253a1%252c%25221%2522%253a1%257d%252c%2522cc%2522%253a1%252c%2522bf_atk%2522%253a0%252c%2522bf_hp%2522%253a0%252c%2522bf_spd%2522%253a0%257d%26qid%3d29018%26res%3d1%26s%3d0%26time%3d2.73%26wc%3d4%26wn%3d4".format(
        hex_now, quest_info['fid'], cid[0])
    r = poster.post_data(url, headers, cookies, payload, **data)
    return r

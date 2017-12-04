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
    payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b6201%2c6003%5d%2c%22sid%22%3a%5b0%2c0%5d%2c%22fid%22%3a%5b3001%5d%2c%22ms%22%3a0%2c%22md%22%3a15072%2c%22sc%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a1%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a1%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a1%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%2c%225%22%3a0%2c%228%22%3a0%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a0%7d%2c%22fj%22%3a0%2c%22fw%22%3a0%2c%22fo%22%3a0%2c%22mlv%22%3a80%2c%22mbl%22%3a150%2c%22udj%22%3a0%2c%22sdmg%22%3a35133%2c%22tp%22%3a12%2c%22gma%22%3a5%2c%22gmr%22%3a5%2c%22gmp%22%3a0%2c%22stp%22%3a0%2c%22uh%22%3a%7b%2210%22%3a2%2c%227%22%3a1%7d%2c%22cc%22%3a1%2c%22bf_atk%22%3a0%2c%22bf_hp%22%3a0%2c%22bf_spd%22%3a0%7d&bl=%5b%7b%22src_cid%22%3a59009%2c%22mana%22%3a2%2c%22use_skill%22%3atrue%7d%2c%7b%22src_cid%22%3a6003%2c%22mana%22%3a1%2c%22use_skill%22%3atrue%7d%2c%7b%7d%2c%7b%7d%5d&blf=%5b%7b%22src_cid%22%3a3001%2c%22mana%22%3a0%2c%22use_skill%22%3afalse%7d%5d&nature=bl%3d%255b%257b%2522src_cid%2522%253a59009%252c%2522mana%2522%253a2%252c%2522use_skill%2522%253atrue%257d%252c%257b%2522src_cid%2522%253a6003%252c%2522mana%2522%253a1%252c%2522use_skill%2522%253atrue%257d%252c%257b%257d%252c%257b%257d%255d%26blf%3d%255b%257b%2522src_cid%2522%253a3001%252c%2522mana%2522%253a0%252c%2522use_skill%2522%253afalse%257d%255d%26bt%3d5459%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b6201%252c6003%255d%252c%2522sid%2522%253a%255b0%252c0%255d%252c%2522fid%2522%253a%255b3001%255d%252c%2522ms%2522%253a0%252c%2522md%2522%253a15072%252c%2522sc%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a1%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a1%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%252c%25225%2522%253a0%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a0%252c%2522fw%2522%253a0%252c%2522fo%2522%253a0%252c%2522mlv%2522%253a80%252c%2522mbl%2522%253a150%252c%2522udj%2522%253a0%252c%2522sdmg%2522%253a35133%252c%2522tp%2522%253a12%252c%2522gma%2522%253a5%252c%2522gmr%2522%253a5%252c%2522gmp%2522%253a0%252c%2522stp%2522%253a0%252c%2522uh%2522%253a%257b%252210%2522%253a2%252c%25227%2522%253a1%257d%252c%2522cc%2522%253a1%252c%2522bf_atk%2522%253a0%252c%2522bf_hp%2522%253a0%252c%2522bf_spd%2522%253a0%257d%26qid%3d220103%26res%3d1%26s%3d0%26time%3d2.63%26wc%3d4%26wn%3d4".format(
        hex_now)
    # payload = generate_payload()
    r = poster.post_data(url, headers, cookies, payload, **data)
    return r


def generate_payload():
    import urllib.parse
    cids = [59008,211]
    payload = {
        'ch' : '',
        'eh' : '',
        'ec' : '',
        'mission' : {"cid":cids,"sid":[0,0,0,0,0,0],"fid":[8866],"ms":0,"md":3855,"sc":{"0":1,"1":1,"2":1,"3":1,"4":1},"es":0,"at":4,"he":1,"da":0,"ba":0,"bu":1,"job":{"0":0,"1":0,"2":7,"3":0,"4":0},"weapon":{"0":2,"1":0,"2":0,"3":0,"4":3,"5":0,"8":2,"9":0,"10":0},"box":2,"um":{"1":3,"2":2,"3":0},"fj":2,"fw":8,"fo":0,"mlv":80,"mbl":7,"udj":0,"sdmg":22136,"tp":6,"gma":9,"gmr":6,"gmp":0,"stp":0,"uh":{"3":2,"6":3,"10":1,"14":1},"cc":1,"bf_atk":0,"bf_hp":0,"bf_spd":0},
        'bl' : [
          {
            "src_cid": cids[0],
            "mana": 8,
            "use_skill": "true"
          },
          {
            "src_cid": cids[1],
            "mana": 5,
            "use_skill": "true"
          },
          {
            "src_cid": cids[2],
            "mana": 5,
            "use_skill": "true"
          },
          {
            "src_cid": cids[3],
            "mana": 5,
            "use_skill": "true"
          },
          {
            "src_cid": cids[4],
            "mana": 5,
            "use_skill": "true"
          },
          {
            "src_cid": cids[5],
            "mana": 5,
            "use_skill": "true"
          }
        ],
        'blf' : [{"src_cid":8866,"mana":2,"use_skill":'true'}]
    }
    query_string = urllib.parse.urlencode(payload)
    query_string = query_string.replace("+", "")
    query_string = query_string.replace("%27true%27", "true")
    query_string = query_string.replace("%27", "%22")
    # print(query_string)
    return query_string
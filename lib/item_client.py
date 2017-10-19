import utils.poster
import utils.global_config


item_mapping = {
    "char": {"id": 90904, "type": "chara_rf", "price": 30, "val": 1},
    "weapon": {"id": 93902, "type": "weapon_rf", "price": 30, "val": 1},
    "ap_fruit": {"id": 1, "type": "item", "price": 10, "val": 1},
    "itm_weapon": {"id": 96019, "type": "weapon_ev", "price": 10, "val": 1},
    "itm_weapon_bow": {"id": 96064, "type": "weapon_ev", "price": 10, "val": 1},
    "itm_weapon_magic": {"id": 96126, "type": "weapon_ev", "price": 10, "val": 1}
}


def buy_item(parameter, sid):
    poster = utils.poster.Poster
    url = '{0}/token'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'kind': parameter['kind'],
        'type': parameter['type'],
        'id': parameter['id'],
        'val': parameter['val'],
        'price': parameter['price'],
        'buy_cnt': parameter['buy_cnt'],
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def buy_ap_fruit(sid):
    card_type = 'ap_fruit'
    return buy_item_with_type(card_type, sid)


def buy_weapon_card(sid):
    card_type = 'weapon'
    return buy_item_with_type(card_type, sid)


def buy_char_card(sid):
    card_type = 'char'
    return buy_item_with_type(card_type, sid)


def buy_item_with_type(card_type, sid):
    poster = utils.poster.Poster
    url = '{0}/token'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'kind': 'item',
        'type': item_mapping[card_type]['type'],
        'id': item_mapping[card_type]['id'],
        'val': item_mapping[card_type]['val'],
        'price': item_mapping[card_type]['price'],
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r


def get_daily_gacha_ticket(sid):
    poster = utils.poster.Poster
    url = '{0}/token'.format(utils.global_config.get_hostname())
    cookies = {'sid': sid}
    headers = {'Cookie': 'sid={0}'.format(sid)}
    data = {
        'kind': 'limit_item',
        'limit_id': 9000,
        'type': 'item',
        'id': 7,
        'val': 1,
        'price': 25,
    }
    r = poster.post_data(url, headers, cookies, payload=None, **data)
    return r

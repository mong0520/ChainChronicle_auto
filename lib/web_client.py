#-*- coding: utf-8 -*-
import requests
import utils.global_config


def get_gacha_page(sid):
    url = "{0}/web/gacha".format(utils.global_config.get_hostname())
    headers = {
        'DeviceWidth': '1024',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'AppVersion': '3.22',
        'user-agent': 'Chronicle/3.2.2 Rev/45834 (Android OS 6.0.1 / API-23)',
        'Accept-Encoding': 'identity',
        'Cookie': 'devicewidth=1024; framewidth=577; devicewidth=1024; framewidth=1024; sid={0}'.format(sid),
        'FrameWidth': '577',
        'Accept-Language': 'zh-tw',
        'Host': '{0}'.format(utils.global_config.get_fqdn()),
        'Accept-Encoding': 'gzip, deflate'

    }
    cookies = {'sid': sid, 'devicewidth':1024, 'framewidth':577}
    r = requests.get(url, headers=headers)
    return r



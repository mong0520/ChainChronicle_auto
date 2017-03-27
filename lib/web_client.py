#-*- coding: utf-8 -*-
import requests


def get_gacha_page(sid):
    url = "http://v272.cc.mobimon.com.tw/web/gacha"
    headers = {
        'DeviceWidth': '1024',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'AppVersion': '2.72',
        'user-agent': 'Chronicle/2.7.2 Rev/45834 (Android OS 6.0.1 / API-23)',
        'Accept-Encoding': 'identity',
        'Cookie': 'devicewidth=1024; framewidth=577; devicewidth=1024; framewidth=1024; sid={0}'.format(sid),
        'FrameWidth': '577',
        'Accept-Language': 'zh-tw',
        'Host': 'v272.cc.mobimon.com.tw',
        'Accept-Encoding': 'gzip, deflate'

    }
    cookies = {'sid': sid, 'devicewidth':1024, 'framewidth':577}
    r = requests.get(url, headers=headers)
    return r



#-*- coding: utf-8 -*-
import requests
import re
import sys
import os
sys.path.append('../')
from lib import session_client
from lib import web_client

def main():
    ret = session_client.login('ANDO822adb47-dd36-41ce-8640-9f17604d0778')
    sid = ret['login']['sid']
    # sid = '4b14221db15836fb30368eaf8319027d'
    data = web_client.get_gacha_page(sid)
    print '{0}'.format(data.text.encode('utf-8'))


if __name__ == '__main__':
    main()

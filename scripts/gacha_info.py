#-*- coding: utf-8 -*-
import requests
import re
import sys
import os
sys.path.append('../')
from lib import session_client
from lib import web_client
#from bs4 import BeautifulSoup

def main():
    try:
        gacha_id = sys.argv[1]
    except:
        gacha_id = 1
    ret = session_client.login('iOS534D3015-63D3-4B02-A081-D810435AE171', 
            'D6F13C92AA9E1561631CFA578A5AB1855EDDB6E28163DC1CBB33454E77152A08')
    sid = ret['login']['sid']
    # sid = '4b14221db15836fb30368eaf8319027d'
    data = web_client.get_gacha_page(sid, gacha_id)
    c = data.text
    print(c)
    # soup = BeautifulSoup(c, 'html.parser')
    # samples = soup.find_all("script", type="text/javascript")
    #for s in samples:
    #    print s.attrs
    #token = 'map_event_gacha_type'
    #content = repr(samples[3].text)
    #idx = content.index(token)
    #print content[idx:].encode('utf-8')

    #print '{0}'.format(data.text.encode('utf-8'))


if __name__ == '__main__':
    main()

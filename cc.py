# -*- coding: utf-8 -*-
import json
import requests
import sys
import time
import logging
import datetime
from logging.handlers import RotatingFileHandler

# Version: 1.0.1
# Date: 2015/7/7
# Author: Mong

class ChainChronicleAutomation():
    def __init__(self):
        self.uid = "ANDOa5f1b8e3-9ad9-40f2-8b5c-57a8b521151d" 
        self.token = "APA91bGTMWur8RYAC0edNtWPxKlaH7KmnRBWf50kmRI2VBE93WQiyxeCMjbtVz75WEIQIDlhE2xdiEtF-RJz57S3Z1duvyCJ3S2Mk7Crf_29HlScIy3I_331XHHAdRDpJDCrK9Oc3IEk"
        self.__initLogger()
        self.sid = None
        self.headers = {        
                'X-Unity-Version': '4.6.5f1',       
                'Device': '0',
                'AppVersion': '2.22',
                'Accept-Encoding': 'identity',
                'user-agent': 'Chronicle/2.2.2 Rev/20320 (Android OS 4.4.4 / API-19 (KTU84P/V6.5.3.0.KXDMICD))',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Platform': '2',
                'Host': 'prod4.cc.mobimon.com.tw',
                'Connection': 'Keep-Alive',
                'Content-Length': '1506'
                }
        self.cardTypes = {0: "角色卡", 1: "武器卡", 2: "鍛造卡", 3: "成長卡"}
        
    def getLogger(self):
        return self.logger
                
    def CC_Login(self):
        # Login and get sid
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': 'INVALID'}
        self.headers = {        
                'Cookie': 'sid=INVALID',                
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436052183%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.uid, self.token)
                }
        post_url = "http://prod4.cc.mobimon.com.tw/session/login?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%22{1}%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d".format(hexNow, int(time.time()), self.uid, self.token)
        r = requests.post(post_url, data=payload, headers=self.headers)
        #print r.text
        self.sid = r.json()['login']['sid']
        self.logger.debug("ChainChronicle Login result = [{0}]".format(r.json()['res']))
        self.logger.debug("session ID = {0}".format(self.sid))

    def CC_PlayQuest(self, qid, count, bRaid, bSell):
        for i in range(0, count):
            #print "Start to play quest:[{0}]".format(i)
            result = self.__getQuest(qid).json()
            #print "...Result = [{0}]".format(result['res'])
            #print result
            if (result['res'] == 103):
                self.logger.warning("體力不足, 使用體力果")
                r = self.__recoverStamina()      
                if r['res'] != 0:           
                    self.logger.debug("恢復體力失敗: {0}".format(r['res']))
                    #print "Trying to buy 1 Stamina Fruit"
                    #self.CC_buyStaminaFruit(1)         
                time.sleep(1) 
                continue    
            result = self.__getBattleResult(qid).json()
            if result['res'] == 0:
                self.logger.debug("#{0} - 任務完成!".format(i))
                #self.logger.debug(result)

                # Sell the treasures
                if bSell:
                    try:
                        for earn in result['body'][1]['data']:
                            # id = earn['id']
                            idx = earn['idx']
                            # self.logger.debug(idx)
                            self.__sellItem(idx)
                    except Exception as e:
                        self.logger.debug("無可販賣卡片")
            elif result['res'] == 1:
                self.logger.debug("#{0} - 任務失敗，已被登出".format(i))
            else:
                self.logger.debug("#{0} - 任務失敗: Error Code = {1}".format(i, result['res']))
            
            #魔神戰
            self.__PlayRaid(bRaid)
            
            time.sleep(1)       
            
        
    def CC_Gacha(self, count, bSell, keptCards):       
        for i in range(0, count):
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),               
                    'nat': "c=1&cnt=14e5c7f82a4&nature=c%3d1%26cnt%3d{0}%26t%3d6&t=6&timestamp={1}".format(hexNow, now)
                    }
            post_url = "http://prod4.cc.mobimon.com.tw/gacha?t=6&c=1&cnt={0}&timestamp={1}".format(hexNow, now)
            payload = "nature=c%3d1%26cnt%3d{0}%26t%3d6".format(hexNow)
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            #print (r.text) 
            try:
                idx = int(r['body'][1]['data'][0]['idx'])
                type = int(r['body'][1]['data'][0]['type'])
                #id = r['body'][1]['data'][0]['id']
                #self.logger.debug("#{0}: Gacha! Result = {1}, Card ID = {2}, Card UID = {3}".format(i, r['res'], id, idx))               
                self.logger.debug("#{0}: 挑戰轉蛋！ 獲得[{1}]一張".format(i, self.cardTypes[type]))                
                if bSell:
                    if not keptCards or type not in keptCards:
                        self.__sellItem(idx)

            except Exception as e:
                self.logger.debug(str(e))
                self.logger.debug("Undefined Error: {0}".format(r['res']))
                self.logger.debug('包包已滿？')    

    
    def CC_buyStaminaFruit(self, count):
        for i in range(0, count):
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),               
                    'nat': "c=1&cnt=14e5c7f82a4&nature=c%3d1%26cnt%3d{0}%26t%3d6&t=6&timestamp={1}".format(hexNow, now)
                    }
            post_url = "http://prod4.cc.mobimon.com.tw/token?kind=item&type=item&id=1&val=2&price=15&cnt={0}&timestamp={1}".format(hexNow, now)
            payload = "nature=cnt%3d{0}%26id%3d1%26kind%3ditem%26price%3d15%26type%3ditem%26val%3d2".format(hexNow)
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            if r['res'] == 0:
                self.logger.debug("#{0}, 購買體力果實完成".format(i))
            else:
                self.logger.debug("#{0}, 購買體力果實失敗, result = {0}".format(i, r['res']))

    def __sellItem(self, idx):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "c=1&cnt=14e5c7f82a4&nature=c%3d1%26cnt%3d{0}%26t%3d6&t=6&timestamp={1}".format(hexNow, now)
                    }
        post_url = "http://prod4.cc.mobimon.com.tw/card/sell?c={0}&cnt={1}&timestamp={2}".format(idx, hexNow, now)
        payload = "nature=c%3d{0}%26cnt%3d{1}".format(idx, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        try:
            self.logger.debug("-> 賣出卡片 {0}, result = {1}".format(idx, r['res']))
        except Exception as e:
            self.logger.error("-> 卡片無法賣出, Error Code = {0}".format(r['res']))

    
    def __getQuest(self, qid):
        # Get Quest     
        now = int(time.time())  
        hexNow = format(now+5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),               
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436043943%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436043943%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.uid, self.token)
                }
        post_url = "http://prod4.cc.mobimon.com.tw/quest/entry?type=4&qid={0}&fid=1690716&pt=0&cnt={1}&timestamp={2}".format(qid, hexNow, now)  
        payload = "nature=cnt%3d{0}%26fid%3d1690716%26pt%3d0%26qid%3d220103%26type%3d4".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies)
        return r
        
    def __getBattleResult(self, qid):
        #qid = '220512'
        # Battle Result
        now = int(time.time())  
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),           
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436043943%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436043943%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.uid, self.token)               
                }
        post_url = "http://prod4.cc.mobimon.com.tw/quest/result?qid={0}&res=1&bt=3206&time=0.00&d=1&s=0&cc=1&wc=4&wn=4&cnt={1}&timestamp={2}".format(qid, hexNow, now)
        payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b7505%2c5033%2c52%2c38%2c7502%2c45%5d%2c%22fid%22%3a4021%2c%22ms%22%3a0%2c%22md%22%3a0%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a1%2c%221%22%3a1%2c%222%22%3a2%2c%223%22%3a1%2c%224%22%3a2%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a1%2c%222%22%3a0%2c%223%22%3a1%2c%224%22%3a2%2c%225%22%3a1%2c%228%22%3a0%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a-1%2c%22fw%22%3a-1%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bt%3d3206%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b7505%252c5033%252c52%252c38%252c7502%252c45%255d%252c%2522fid%2522%253a4021%252c%2522ms%2522%253a0%252c%2522md%2522%253a0%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a1%252c%25221%2522%253a1%252c%25222%2522%253a2%252c%25223%2522%253a1%252c%25224%2522%253a2%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a1%252c%25224%2522%253a2%252c%25225%2522%253a1%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a-1%252c%2522fw%2522%253a-1%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26qid%3d220103%26res%3d1%26s%3d0%26time%3d0.00%26wc%3d4%26wn%3d4".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies)        
        #print (r.text)
        return r    

    def __getRaidBossId(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "cnt=14e64896ccb&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
            }
        post_url = "http://prod4.cc.mobimon.com.tw/raid/list?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()     
        #self.logger.debug("Raw data = {0}".format(r))
        try:
            #self.logger.debug("Raid Boss ID: [{0}]".format(r['body'][0]['data'][0]['boss_id']))
            self.logger.debug(u"魔神來襲！魔神等級: [{0}]".format(r['body'][0]['data'][0]['boss_param']['lv']))
            return r['body'][0]['data'][0]['boss_id']
        except Exception as e:
            self.logger.debug(u"未觸發魔神戰")
            return None

    def __PlayRaid(self, bRaid):
        if bRaid:
            bossId = self.__getRaidBossId()
            if bossId:
                r = self.__getRaidRequest(bossId)
                if r['res'] == 0:
                    self.__getRaidResult(bossId)
                    self.__getRaidBonus(bossId)
                elif r['res'] == 104:
                    self.logger.debug(u"魔神戰體力不足")
                elif r['res'] == 603:
                    self.logger.debug(u"魔神戰逾時")
                else:
                    self.logger.debug("Unknown Error: {0}".format(r['res']))
            else:
                pass
        else:
            pass
                      
    
    def __getRaidRequest(self, bossId):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "bid={0}&cnt={1}&fid=1913206&nature=bid%3d{0}%26cnt%3d{1}%26fid%3d1913206%26pt%3d0%26use%3d1&pt=0&timestamp={2}&use=1".format(bossId, hexNow, now)
            }
        post_url = "http://prod4.cc.mobimon.com.tw/raid/entry?bid={0}&use=1&fid=1913206&pt=0&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
        payload = "nature=bid%3d{0}%26cnt%3d{1}%26fid%3d1913206%26pt%3d0%26use%3d1".format(bossId, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()      
        #self.logger.debug("Get Raid Request result = {0}".format(r['res']))
        return r
        
    def __getRaidResult(self, bossId):        
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "bid={0}&cnt={1}&damage=994500&mission=%7b%22cid%22%3a%5b1032%2c57%2c7505%2c3022%2c1021%2c38%5d%2c%22fid%22%3a43%2c%22ms%22%3a0%2c%22md%22%3a149140%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a1%2c%22fw%22%3a3%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bid%3d{0}%26cnt%3d{1}%26damage%3d994500%26mission%3d%257b%2522cid%2522%253a%255b1032%252c57%252c7505%252c3022%252c1021%252c38%255d%252c%2522fid%2522%253a43%252c%2522ms%2522%253a0%252c%2522md%2522%253a149140%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%252c%25225%2522%253a1%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a1%252c%2522fw%2522%253a3%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26res%3d1%26t%3d15&res=1&t=15&timestamp={2}".format(bossId, hexNow, now)
            }
        post_url = "http://prod4.cc.mobimon.com.tw/raid/result?bid={0}&res=1&damage=9994500&t=15&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
        payload = "mission=%7b%22cid%22%3a%5b1032%2c57%2c7505%2c3022%2c1021%2c38%5d%2c%22fid%22%3a43%2c%22ms%22%3a0%2c%22md%22%3a149140%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a1%2c%22fw%22%3a3%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bid%3d{0}%26cnt%3d{1}%26damage%3d994500%26mission%3d%257b%2522cid%2522%253a%255b1032%252c57%252c7505%252c3022%252c1021%252c38%255d%252c%2522fid%2522%253a43%252c%2522ms%2522%253a0%252c%2522md%2522%253a149140%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%252c%25225%2522%253a1%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a1%252c%2522fw%2522%253a3%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26res%3d1%26t%3d15".format(bossId, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()                
        #self.logger.debug("Get Raid Play result = {0}".format(r['res']))
        return r
    
    
    def __getRaidBonus(self, bossId):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "bid={0}&cnt={1}&nature=bid%3d{0}%26cnt%3d{1}&timestamp={2}".format(bossId, hexNow, now)
            }
        post_url = "http://prod4.cc.mobimon.com.tw/raid/record?bid={0}&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
        payload = "nature=bid%3d{0}%26cnt%3d{1}".format(bossId, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()                        
        self.logger.debug(u"{0}".format(r['title']))
        return r
    
    def __recoverStamina(self):
        now = int(time.time())  
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),               
                'nat': "cnt=14e5b4ed1b3&item_id=1&nature=cnt%3d{0}%26item_id%3d1%26type%3d1&timestamp={1}&type=1".format(hexNow, now)               
                }
        post_url = "http://prod4.cc.mobimon.com.tw/user/recover_ap?type=1&item_id=1&cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}%26item_id%3d1%26type%3d1".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()     
        if r['res'] == 0:
            self.logger.debug("體力完全回復")
        elif r['res'] == 703:
            self.logger.debug("體力果石不足，無法回復體力")
        else:
            self.logger.debug("體力無法回復, Error Code:{0}".format(r['res']))
        return r    

    def __initLogger(self):
        fileFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            ' - %(message)s', datefmt='%B %d %H:%M:%S')
        
        self.logger = logging.getLogger("Chain Chronicle")
        self.logger.setLevel(logging.DEBUG)
        
        rh = RotatingFileHandler("cc.log", maxBytes=1024*5, backupCount=3)
        rh.setLevel(logging.DEBUG)
        rh.setFormatter(fileFormatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(consoleFormatter)

        self.logger.addHandler(rh)   
        self.logger.addHandler(console)   
        
    
    def printUsage(self):
        print "cc.py -type [gacha|quest|buy] -qid quest_id -count n -sell [0|1] -raid [0|1] -keep [0,1,2,3]\n"
        print "gacha: play gacha for [count] times, if [sell] is 1, then sell it immediately.\n"+\
                " Specified card type will NOT be sold by assign the card type to [keep], seperate by ','" +\
                "0 = 角色卡, 1 = 武器卡, 2 = 鍛造卡, 3 = 成長卡\n" +\
                "example: python cc.py -type gacha -count 200 keep 2,3\n"
        print "quest: play quest with [qid] for [count] times, play Raid game if raid = 1, if [sell] is 1, then sell it immediately\n"
        print "buy: buy [count] Stamina Fruits"

if __name__ == "__main__":
    cc = ChainChronicleAutomation()
    #qid = 220512 #50wave挑戰者洞窟
    #qid = 220804 #日照的大海
    
    type = None
    qid = 0
    count = 1
    bSell = 0
    bRaid = 0
    keptCards = None
    
    if len(sys.argv) < 3: 
        cc.printUsage()
        sys.exit(0)
    else:
        for i in range(0, len(sys.argv)):
            if sys.argv[i] == "-type":
                type = sys.argv[i+1]
            if sys.argv[i] == "-buy":
                type = sys.argv[i+1]
            if sys.argv[i] == "-qid":   
                qid = int(sys.argv[i+1])
            if sys.argv[i] == "-count": 
                count = int(sys.argv[i+1])
            if sys.argv[i] == "-sell":
                bSell = int(sys.argv[i+1])
            if sys.argv[i] == "-raid":
                bRaid = int(sys.argv[i+1])
            if sys.argv[i] == "-keep":
                keptCards = [ int(n) for n in sys.argv[i+1].split(',') ]

    logger = cc.getLogger()            
    now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    logger.debug("#Start at: {0}".format(now))
    cc.CC_Login()

    if type == 'gacha':     
        cc.CC_Gacha(count, bSell, keptCards)
    elif type == 'quest':       
        if qid:
            cc.CC_PlayQuest(qid, count, bRaid, bSell)         
        else:
            cc.printUsage();
    elif type == 'buy':
        cc.CC_buyStaminaFruit(count)
    else:
        logger.debug("Unsupported type:[{0}]".format(type))

    now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M%S')
    logger.debug("#End at: {0}".format(now))

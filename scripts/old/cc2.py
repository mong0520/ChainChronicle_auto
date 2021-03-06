# -*- coding: utf-8 -*
import ConfigParser
import datetime
import json
import logging
import os
import sys
import time
from Queue import Queue
from logging.handlers import RotatingFileHandler
from random import randint
from threading import Thread

import requests
from pymongo import MongoClient

from utils import poster


class ChainChronicleAutomation():
    def __init__(self, configFile):
        #self.config['General']['uid'] = "ANDO4779bf78-f0f7-4a16-8d41-3c0d9ab46e0c"
        #self.config['General']['token'] = "APA91bEAKkkmD_eJ07r_NjRMRKJ2keH1A1Ju8mC2MDd9Iu9Bogxoy-HBl8SlCJJmMEM-aCMxnMEDNr-AC5TIiKmUHGRkk-lO1ypSdZhE8PhlQLjvBub3t81kwwwxIDQPw6CsarSI_BJ8"
        log_tailname = os.path.basename(os.path.splitext(configFile)[0])
        self.__initLogger(log_tailname)
        self.poster = poster.Poster()
        self.sid = None
        self.headers = {
                'X-Unity-Version': '4.6.5f1',
                'Device': '0',
                'AppVersion': '2.22',
                'Accept-Encoding': 'identity',
                'user-agent': 'Chronicle/2.2.2 Rev/20320 (Android OS 4.4.4 / API-19 (KTU84P/V6.5.3.0.KXDMICD))',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Platform': '2',
                'Host': 'v272.cc.mobimon.com.tw',
                'Connection': 'Keep-Alive',
                'Content-Length': '1506'
                }
        # self.cardTypes = {0: "角色卡", 1: "武器卡", 2: "鍛造卡", 3: "成長卡"}
        self.cardTypeMapping = {"grwoth":[{"name": u"成長卡"}, {"cid": [90010,90011,90012,90013,90014]}],
                                "weapon":[{"name": u"武器卡"}, {"cid": [93006,93007,93008,93009, 93010, 93011,93021,93022,93023]}],
            }
        self.__initDb()
        self.__loadConfig(configFile)

    def __initDb(self):
        # pass
        client = MongoClient('lineage.twbbs.org', 27017)
        # client = MongoClient('54.64.174.97', 27017)
        client = MongoClient('127.0.0.1', 27017)


        #client.the_database.authenticate('admin', 'mong730520', source = 'admin')
        self.db = client.cc

    def __loadConfig(self, configFile):
        try:
            self.config = {"General":{}, "Quest":{}, "Gacha":{} ,"Buy":{}, "RaidGacha":{}, "Explorer":{}}
            config = ConfigParser.ConfigParser()
            config.read(configFile)

            self.config['General']['uid'] = config.get('General', 'Uid')
            self.config['General']['token'] = config.get('General', 'Token')
            self.config['Quest']['quest_id'] = config.get('Quest', 'QuestId')
            # self.config['Quest']['type'] = config.get('Quest', 'QuestId').split(",")[0]
            # self.config['Quest']['id'] = config.get('Quest', 'QuestId').split(",")[1]
            self.config['Quest']['count'] = config.getint('Quest', 'Count')
            self.config['Quest']['sell'] = config.getint('Quest', 'AutoSell')
            self.config['Quest']['raid'] = config.getint('Quest', 'AutoRaid')
            self.config['Quest']['max_event_point'] = config.getint('Quest', 'MaxEventPoint')

            self.config['Gacha']['count'] = config.getint('Gacha', 'Count')
            self.config['Gacha']['sell'] = config.getint('Gacha', 'AutoSell')
            self.config['Gacha']['type'] = config.getint('Gacha', 'Type')
            self.config['Gacha']['keep_cards'] = config.get('Gacha', 'KeepCards')

            # self.config['RaidGacha']['count'] = config.getint('RaidGacha', 'Count')
            # self.config['RaidGacha']['sell'] = config.getint('RaidGacha', 'AutoSell')
            # self.config['RaidGacha']['keepCardId'] = config.getint('RaidGacha', 'KeepCardId')


            try:
                self.config['Buy']['count'] = config.getint('Buy', 'Count')
            except:
                self.config['Buy']['count'] = 1

            try:
                self.config['Buy']['type'] = config.get('Buy', 'Type')
            except:
                self.config['Buy']['type'] = 0

            try:
                self.config['General']['RetryDurtion'] = config.getint('General', 'RetryDuration')
            except:
                self.config['General']['RetryDurtion'] = 10

            try:
                self.config['General']['Delay'] = config.getint('General', 'Delay')
            except:
                self.config['General']['Delay'] = 0

            try:
                self.config['Explorer']['area'] = config.get('Explorer', 'area')
            except:
                self.config['Explorer']['area'] = 0

        except Exception as e:
            raise
            sys.exit(0)

    def getConfigDictionary(self):
        return self.config

    def getLogger(self):
        return self.logger

    def CC_GetAllData(self):
        url = "http://v272.cc.mobimon.com.tw/user/all_data"
        data = {}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        cookies = {'sid': self.sid}
        # self.poster.set_header(headers)
        # self.poster.set_cookies(cookies)
        ret = self.poster.post_data(url, headers, cookies, **data)
        return ret

    def CC_Login(self):
        # Login and get sid
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': 'INVALID'}
        self.headers = {
                'Cookie': 'sid=INVALID',
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436052183%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.config['General']['uid'], self.config['General']['token'])
                }
        post_url = "http://v272.cc.mobimon.com.tw/session/login?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%22{1}%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d".format(hexNow, int(time.time()), self.config['General']['uid'], self.config['General']['token'])
        r = requests.post(post_url, data=payload, headers=self.headers)
        # self.logger.debug(r)
        try:
            self.sid = r.json()['login']['sid']
        except Exception as e:
            self.logger.error("無法登入, Message = {0}".format(r.json()['msg']))
            sys.exit(0)

    def CC_PlayQuest(self, qtype, qid, count, bRaid, bSell, maxEventPoint):
        current = 0
        bInfinte = False

        if count == -1:
            bInfinte = True
        self.logger.debug("Count = {0}".format(count))
        while True:
            current = current + 1
            self.CC_GetPresents(sell=False)
            #time.sleep(0.5)
            if current > count and not bInfinte:
                break
            print "Start to play quest:[{0}]".format(qid)
            result = self.__getQuest(qtype, qid)
            #print "...Result = [{0}]".format(result['res'])
            #print result
            if (result['res'] == 103):
                self.logger.warning("體力不足, 使用體力果")
                r = self.__recoverStamina()
                if r['res'] != 0:
                    self.logger.warning("恢復體力失敗: {0}".format(r['res']))
                    # sys.exit(0)
                    self.logger.info("購買體力果實(1)...")
                    r = self.CC_buyStaminaFruit(1)
                    if r['res'] == 0:
                        self.logger.debug("購買體力果實完成")
                    else:
                        self.logger.warning("購買體力果實失敗, result = {0}".format(r['res']))
                        self.logger.info("開始友情抽換戒")
                        self.CC_Gacha(6, 20, 1, None)
                time.sleep(1)
                current -= 1
                continue
            if self.config['General']['Delay'] > 0:
                # self.logger.debug(self.config['General']['Delay'])
                random_salt = randint(0,10)
                # random 0 ~ 99 second
                sleep_in_sec = 60 * self.config['General']['Delay'] + random_salt
                self.logger.info("等待{0}秒後完成戰鬥...".format(sleep_in_sec))
                time.sleep(sleep_in_sec)
            result = self.__getBattleResult(qid).json()
            if result['res'] == 0:
                self.logger.info(u"#{0} - Quest is completed!".format(current))
                #self.logger.debug(result)
                # 踏破活動
                try:
                    eventPoint = result['body'][2]['data']['point']
                    feverRate = 1.0
                    self.logger.info("目前戰功：%s" % eventPoint)
                    try:
                        feverRate = result['earns']['treasure'][0]['fever']
                    except Exception as e:
                        pass
                    self.logger.debug("目前戰功倍率：%s" % feverRate)

                    if (maxEventPoint and eventPoint >= maxEventPoint):
                        self.logger.warning("超過最大戰功設定上限")
                        return
                except Exception as e:
                    pass

                # Sell the treasures
                if bSell:
                    try:
                        for earn in result['body'][1]['data']:
                            # id = earn['id']
                            idx = earn['idx']
                            # self.logger.debug(idx)
                            r = self.__sellItem(idx)
                            if r['res'] == 0:
                                self.logger.debug("\t-> 賣出卡片 {0}, result = {1}".format(idx, r['res']))
                            else:
                                self.logger.error("\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
                                sys.exit(0)
                    except Exception as e:
                        self.logger.warning(u"無可販賣卡片")
            elif result['res'] == 1:
                self.logger.warning("#{0} - 戰鬥失敗，已被登出".format(current))
                sleepSec = 60 * self.config['General']['RetryDurtion']
                self.logger.info("等待{0}分鐘後再試...".format(sleepSec/60))
                time.sleep(sleepSec)
                self.CC_Login()
                #sys.exit(0)
            else:
                self.logger.error("#{0} - 戰鬥失敗: Error Code = {1}".format(current, result['res']))
                self.logger.debug(result)
                self.logger.debug("Retry")
                current -= 1
                time.sleep(1)

            #魔神戰
            self.__PlayRaid(bRaid)

            # 避免資料不正常，需要sleep一下
            time.sleep(0.7)

    def CC_SetPassword(self, password):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
                }
        post_url = "http://v272.cc.mobimon.com.tw/user/get_account?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug(r)

        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}%26pass%3d{2}&pass={2}&timestamp={1}".format(hexNow, now, password)
                }
        post_url = "http://v272.cc.mobimon.com.tw/user/set_password?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "pass={0}&nature=cnt%3d{1}%26pass%3d{0}".format(password, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()


        print r

    def CC_Gacha(self, gType, count, bSell, keptCards):
        sleep_time = 0
        for i in range(0, count):
            # time.sleep(0.25)
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            if gType == 3: #魔神轉蛋
                batchCount = 10
                sleep_time = 5
                # 魔神轉蛋不sleep會出現error
            else:
                batchCount = 1
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "c={2}&cnt=14e5c7f82a4&nature=c%3d1%26cnt%3d{0}%26t%3d6&t=6&timestamp={1}".format(hexNow, now, batchCount)
                    }
            post_url = "http://v272.cc.mobimon.com.tw/gacha?t={2}&c={3}&cnt={0}&timestamp={1}".format(hexNow, now, gType, batchCount)
            payload = "nature=c%3d{0}%26cnt%3d{1}%26t%3d6".format(batchCount, hexNow)

            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            time.sleep(sleep_time)
            # self.logger.debug(r)
            # sys.exit(0)
            if r['res'] == 0:
                try:
                    for record in r['body'][1]['data']:
                    # for record in r:
                        #print record
                        #print r['body'][1]
                        idx = record['idx']
                        # id = record['id']
                        # type = record['type']
                        # print r
                        # print r['body'][1]['data']
                        # print record
                        #idx = self.find_key(r, 'idx')
                        id = self.find_key(r, 'id')
                        # type = self.find_key(r, 'type')
                        # print id, idx
                        cardName = ""
                        if id in self.cardTypeMapping['grwoth'][1]['cid']:
                            cardName = self.cardTypeMapping['grwoth'][0]["name"]
                        elif id in self.cardTypeMapping['weapon'][1]['cid']:
                            cardName = self.cardTypeMapping['weapon'][0]["name"]
                        else:
                            try:
                                # cardName = self.db.charainfo.find_one({"cid": id})['name']
                                cardName = id
                            except:
                                self.logger.warning("無法找到角色卡片名稱，請檢查是否有新卡或是DB線連狀態")
                                cardName = id

                        self.logger.debug(u"#{0}: 轉蛋開始！ 獲得[{1}]一張".format(i, cardName))
                        if bSell and (not keptCards or id not in keptCards):
                                r = self.__sellItem(idx)
                                if r['res'] == 0:
                                    self.logger.debug(u"#{0}: 賣出卡片".format(i))
                                else:
                                    self.logger.error(u"\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
                                    sys.exit(0)

                except KeyError as e:
                    self.logger.error("Key Error:{0}, 找不到卡片idx, 可能是包包已滿，或是卡片是新的".format(e))
                    sys.exit(0)
                except Exception as e:
                    raise
                    self.logger.error("Undefined Error: {0}".format(r['res']))
                    self.logger.error(r)
                    sys.exit(0)
            elif r['res'] == 703:
                self.logger.error("聖靈幣不足")
                sys.exit(0)
            else:
                self.logger.error("未定義的錯誤:{0}, {1}".format(r['res'], r['msg']))
                sys.exit(0)



    def find_key(self, d, key):
        for k, v in d.iteritems():
            if k == key: return v
            if isinstance(v, dict):
                t = self.find_key(v, key)
                if t: return t
            elif isinstance(v, list):
                for p in v:
                    t = self.find_key(p, key)
                    if t: return t

        return None

    def CC_buyItem(self, item_type, count):
        r = None
        item_mapping = dict()
        item_mapping = {
            "char": {"id": 90904, "type": "chara_rf", "price": 30, "val": 1},
            "weapon": {"id": 93902, "type": "weapon_rf", "price": 30, "val": 1}
        }
        self.logger.debug(item_mapping[item_type])
        for i in range(0, count):
            self.logger.debug(u"#{0} 購買道具".format(i+1))
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "cnt={0}&id={2}&kind=item&nature=cnt%3d{0}%26id%3d{2}%26kind%3ditem%26price%3d30%26type%3d{3}%26val%3d1&price=30&timestamp={1}&type={3}&val=1".format(hexNow, now, item_mapping[item_type]['id'], item_mapping[item_type]['type'])
                    }
            post_url = "http://v272.cc.mobimon.com.tw/token?kind=item&type={2}&id={3}&val={4}&price={5}&cnt={0}&timestamp={1}".format(hexNow, now, item_mapping[item_type]['type'], item_mapping[item_type]['id'], item_mapping[item_type]['val'], item_mapping[item_type]['price'])
            payload = "nature=cnt%3d{0}%26id%3d{1}%26kind%3ditem%26price%3d{2}%26type%3d{3}%26val%3d{4}".format(hexNow, item_mapping[item_type]['id'], item_mapping[item_type]['price'], item_mapping[item_type]['type'], item_mapping[item_type]['val'])
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            #self.logger.debug(post_url)
            #self.logger.debug(payload)
            #self.logger.debug(self.headers)
            if(r['res']!=0):
                self.logger.warning("購買角色成長卡失敗, ErrorCode = {0}".format(r['res']))
                return r
            else:
                self.logger.debug(u"\t-> 完成")
        return r

    def CC_buyStaminaFruit(self, count):
        r = None
        for i in range(0, count):
            self.logger.debug("#{0} 購買體力果實".format(i+1))
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid)
                    }
            post_url = "http://v272.cc.mobimon.com.tw/token?kind=item&type=item&id=1&val=1&price=10&cnt={0}&timestamp={1}".format(hexNow, now)
            payload = "nature=cnt%3d{0}%26id%3d1%26kind%3ditem%26price%3d10%26type%3ditem%26val%3d1".format(hexNow)
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            if(r['res']!=0):
                self.logger.warning("購買體力果實失敗, ErrorCode = {0}".format(r['res']))
                return r
            else:
                self.logger.debug("\t-> 完成")
        return r

    def CC_explorer(self, explorer_idx, area, idx, pickup=1):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        # area = "0"
        cookies = {'sid': self.sid}
        # idx = "582439944"
        helper1 = "588707"
        helper2 = "1913206"
        # pickup = 0
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "card_idx={2}&cnt={0}&explorer_idx={6}&helper1={3}&helper2={4}&interval=1&"\
                "location_id={5}&nature=card_idx%3d{2}%26cnt%3d{0}%26explorer_idx%3d1%26helper1%3d{3}%26helper2%3d{4}%26"\
                "interval%3d1%26location_id%3d{5}%26pickup%3d{7}&pickup={7}&timestamp={1}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)
                }
        post_url = "http://v272.cc.mobimon.com.tw/explorer/entry?explorer_idx={6}&location_id={5}&card_idx={2}&pickup" \
        "={7}&interval=1&helper1={3}&helper2={4}&cnt={0}&timestamp={1}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)

        payload = "nature=card_idx%3d{2}%26cnt%3d{0}%26explorer_idx%3d{6}%26helper1%3d{3}%26helper2%3d{4}%26interval%3d1%26location_id%3d{5}%26pickup%3d{7}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug(json.dumps(r))
        # self.logger.debug(json.dumps(r['res']))

        if r['res'] == 2311:
            # self.logger.debug(u"pickup value error, retry")
            self.CC_explorer(explorer_idx, area, idx, pickup=0)
        elif r['res'] == 0:
            self.logger.debug("探索開始!")
        else:
            self.logger.error("未知的探索錯誤:{0}".format(r['res']))
        return r['res']

    def CC_explorer_result(self, explorer_idx):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        # explorer_idx = "1"
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&explorer_idx={2}&nature=cnt%3d{0}%26explorer_idx%3d{2}&timestamp={1}".format(hexNow, now, explorer_idx)
                }
        post_url = "http://v272.cc.mobimon.com.tw/explorer/result?explorer_idx={2}&cnt={0}&timestamp={1}".format(hexNow, now, explorer_idx)

        payload = "nature=cnt%3d{0}%26explorer_idx%3d{2}".format(hexNow, now, explorer_idx)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug("取得探索成果!")
        self.logger.debug(json.dumps(r))
        return r

    def CC_explorer_get_pickup(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        # explorer_idx = "1"
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
                }
        post_url = "http://v272.cc.mobimon.com.tw/explorer/list?cnt={0}&timestamp={1}".format(hexNow, now)

        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        return r


    def CC_explorer_cancel(self, explorer_idx):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        # explorer_idx = "1"
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&explorer_idx={2}&nature=cnt%3d{0}%26explorer_idx%3d{2}&timestamp={1}".format(hexNow, now, explorer_idx)
                }
        post_url = "http://v272.cc.mobimon.com.tw/explorer/cancel?explorer_idx={2}&cnt={0}&timestamp={1}".format(hexNow, now, explorer_idx)

        payload = "nature=cnt%3d{0}%26explorer_idx%3d{2}".format(hexNow, now, explorer_idx)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug(json.dumps(r))
        return r

    def CC_Subjugation(self, jid):
        while True:
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}

            # Check
            # self.logger.debug("Check Subjugation")
            # self.headers = {
            #         'Cookie': 'sid={0}'.format(self.sid),
            #         'nat': "cnt={0}&jid={2}&nature=cnt%3d{0}%26jid%3d{2}&timestamp={1}".format(hexNow, now, jid)
            #         }
            # post_url = "http://v272.cc.mobimon.com.tw/subjugation/check_participant?jid={2}&cnt={0}&timestamp={1}".format(hexNow, now, jid)
            # payload = "nature=cnt%3d{0}%26jid%3d{1}".format(hexNow, jid)
            # r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()

            # get ecnt
            # r = cc.CC_GetAllData()
            # ecnt = r['body'][18]['data']['reached_expedition_cnt'] + 1
            ecnt = 0
            self.logger.info(u"第{0}次討伐".format(ecnt))
            # sys.exit(0)

            # Try
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            self.logger.debug(u"取得討伐戰資料")
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "brave=0&cnt={0}&ecnt={3}&jid={2}&nature=brave%3d0%26cnt%3d{0}%26ecnt%3d{3}%26jid%3d{2}&timestamp={1}".format(hexNow, now, jid, ecnt)
                    }
            post_url = "http://v272.cc.mobimon.com.tw/subjugation/try?jid={2}&ecnt={3}&brave=0&cnt={0}&timestamp={1}".format(hexNow, now, jid, ecnt)

            payload = "nature=brave%3d0%26cnt%3d{0}%26ecnt%3d{2}%26jid%3d{1}".format(hexNow, jid, ecnt)
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            if r['res'] == 1916:
                self.logger.warning("Not enough brave, exit")
                break
            elif r['res'] == 1917:
                self.logger.warning(u"已經在討伐中")
                self.logger.debug(r)

            # check r, maybe already tried, then call proceed to get base_id

            # self.logger.debug(r)
            # Get base id
            self.logger.debug(u"取得關卡id")
            base_id_list = []
            wave_list = []
            for data in r['body'][1]['data']:
                base_id_list.append(data['base_id'])
                wave_list.append(data['max_wave'])
            self.logger.debug(u"關卡id = {0}".format(base_id_list))
            # Start
            pt_cid = [5002, 6043, 7017, 41]
            pt_cids = [
                [6042, 6043, 5047],
                [5002, 5049, 61],
                [69, 5057, 6],
                [2049,2, 4]
            ]
            for idx, bid in enumerate(base_id_list):
                now = int(time.time()*1000)
                hexNow = format(now + 5000, 'x')
                self.logger.debug(u"Using Party {0}".format(idx))

                # Start entry
                self.logger.debug(u"開始討伐")
                self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "bid={3}&brave=0&cnt={0}&fid=383974&full=0&jid={2}&nature=bid%3d{3}%26brave%3d0%26cnt%3d{0}%26fid%3d383974%26full%3d0%26jid%3d{2}%26pt%3d0&pt={4}&timestamp={1}".format(hexNow, now, jid, bid, idx)}
                post_url = "http://v272.cc.mobimon.com.tw/subjugation/entry?jid={2}&bid={3}&pt={4}&fid=383974&full=0&brave=0&cnt={0}&timestamp={1}".format(hexNow, now, jid, bid, idx)
                payload = "nature=bid%3d{3}%26brave%3d0%26cnt%{0}%26fid%3d383974%26full%3d0%26jid%3d{2}%26pt%3d{4}".format(hexNow, now, jid, bid, idx)

                self.logger.debug(u'討伐關卡: {0}'.format(bid))
                r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
                # self.logger.debug("Start entry = {0}".format(r))

                # Get Result
                now = int(time.time()*1000)
                hexNow = format(now + 5000, 'x')
                self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "bid={bid}&bt=7056&cc=1&cnt={cnt}&d=1&jid={jid}&mission=%7b%22cid%22%3a%5b{cid0}%2c{cid1}%2c{cid2}%5d%2c%22sid%22%3a%5b0%2c0%2c0%5d%2c%22fid%22%3a6043%2c%22ms%22%3a1%2c%22md%22%3a2476%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%2c%225%22%3a0%2c%228%22%3a0%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a2%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a0%2c%22fw%22%3a0%2c%22fo%22%3a0%2c%22cc%22%3a1%2c%22bf_atk%22%3a0%2c%22bf_hp%22%3a0%2c%22bf_spd%22%3a0%7d&nature=bid%3d{bid}%26bt%3d7056%26cc%3d1%26cnt%3d{cnt}%26d%3d1%26jid%3d{jid}%26mission%3d%257b%2522cid%2522%253a%255b{cid0}%252c{cid1}%252c{cid2}%255d%252c%2522sid%2522%253a%255b0%252c0%252c0%255d%252c%2522fid%2522%253a6043%252c%2522ms%2522%253a1%252c%2522md%2522%253a2476%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%252c%25225%2522%253a0%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a2%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a0%252c%2522fw%2522%253a0%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%252c%2522bf_atk%2522%253a0%252c%2522bf_hp%2522%253a0%252c%2522bf_spd%2522%253a0%257d%26res%3d1%26s%3d0%26time%3d1.80%26wc%3d{wc}&res=1&s=0&time=1.80&timestamp={now}&wc={wc}".format(cnt=hexNow, now=now, jid=jid, bid=bid, cid0=pt_cids[idx][0], cid1=pt_cids[idx][1], cid2=pt_cids[idx][1], wc=wave_list[idx])
                    }

                post_url = "http://v272.cc.mobimon.com.tw/subjugation/result?res=1&jid={2}&bid={3}&wc={4}&bt=6176&cc=1&time=1.68&d=1&s=1&cnt={0}&timestamp={1}".format(hexNow, now, jid, bid, wave_list[idx])

                payload = "mission=%7b%22cid%22%3a%5b{cid0}%2c{cid1}%2c{cid2}%5d%2c%22sid%22%3a%5b0%2c0%2c0%5d%2c%22fid%22%3a6043%2c%22ms%22%3a1%2c%22md%22%3a2476%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%2c%225%22%3a0%2c%228%22%3a0%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a2%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a0%2c%22fw%22%3a0%2c%22fo%22%3a0%2c%22cc%22%3a1%2c%22bf_atk%22%3a0%2c%22bf_hp%22%3a0%2c%22bf_spd%22%3a0%7d&nature=bid%3d{bid}%26bt%3d7056%26cc%3d1%26cnt%3d{cnt}%26d%3d1%26jid%3d{jid}%26mission%3d%257b%2522cid%2522%253a%255b{cid0}%252c{cid1}%252c{cid2}%255d%252c%2522sid%2522%253a%255b0%252c0%252c0%255d%252c%2522fid%2522%253a6043%252c%2522ms%2522%253a1%252c%2522md%2522%253a2476%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%252c%25225%2522%253a0%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a2%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a0%252c%2522fw%2522%253a0%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%252c%2522bf_atk%2522%253a0%252c%2522bf_hp%2522%253a0%252c%2522bf_spd%2522%253a0%257d%26res%3d1%26s%3d0%26time%3d1.80%26wc%3d{wc}".format(cnt=hexNow, now=now, jid=jid, bid=bid, cid0=pt_cids[idx][0], cid1=pt_cids[idx][1], cid2=pt_cids[idx][1], wc=wave_list[idx])
                r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
                # self.logger.debug("End entry = {0}".format(r))
                self.logger.debug(u'討伐關卡: {0} 完成'.format(bid))


    def __sellItem(self, idx):
        url = 'http://v272.cc.mobimon.com.tw/card/sell'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {
            'c': idx
        }
        r = self.poster.post_data(url, headers, cookies, **data)
        return r


    def __getQuest(self, qtype, qid):
        # Get Quest
        url = 'http://v272.cc.mobimon.com.tw/quest/entry'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {
            'oc': 1,
            'type': qtype,
            'qid': qid,
            'fid': 1965350,
            'pt': 0
        }
        r = self.poster.post_data(url, headers, cookies, **data)
        return r

    def __getBattleResult(self, qid):
        # Battle Result
        # url = 'http://v272.cc.mobimon.com.tw/quest/entry'
        # cookies = {'sid': self.sid}
        # headers = {'Cookie': 'sid={0}'.format(self.sid)}
        # data = {
        #     'qid': qid,
        #     'res': 1,
        #     'bt': 1200,
        #     'time': '0.00',
        #     'd': 1,
        #     's': 1,
        #     'cc': 1,
        #     'wc': 5,
        #     'wn': 5
        # }
        # r = self.poster.post_data(url, headers, cookies, **data)

        now = int(time.time())
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%2522143198601943%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%22143198601943%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1851%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.config['General']['uid'], self.config['General']['token'])
                }
        post_url = "http://v272.cc.mobimon.com.tw/quest/result?qid={0}&res=1&bt=1200&time=0.00&d=1&s=1&cc=1&wc=5&wn=5&cnt={1}&timestamp={2}".format(qid, hexNow, now)
        payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b7505%2c5033%2c52%2c38%2c7502%2c45%5d%2c%22fid%22%3a1965350%2c%22ms%22%3a1%2c%22md%22%3a200001%2c%22sc%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a0%7d%2c%22es%22%3a1%2c%22at%22%3a1%2c%22he%22%3a1%2c%22da%22%3a1%2c%22ba%22%3a1%2c%22bu%22%3a1%2c%22job%22%3a%7b%220%22%3a1%2c%221%22%3a1%2c%222%22%3a2%2c%223%22%3a1%2c%224%22%3a2%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a2%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a1%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a0%7d%2c%22fj%22%3a-1%2c%22fw%22%3a-1%2c%22fo%22%3a1%2c%22cc%22%3a1%7d&nature=bt%3d1200%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b7505%252c5033%252c52%252c38%252c7502%252c45%255d%252c%2522fid%2522%253a1965350%252c%2522ms%2522%253a0%252c%2522md%2522%253a200000%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a1%252c%25221%2522%253a1%252c%25222%2522%253a2%252c%25223%2522%253a1%252c%25224%2522%253a2%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a1%252c%25224%2522%253a2%252c%25225%2522%253a1%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a-1%252c%2522fw%2522%253a-1%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26qid%3d220103%26res%3d1%26s%3d0%26time%3d0.00%26wc%3d5%26wn%3d5".format(hexNow)

        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies)
        #print (r.text)
        return r

    def __getCardInfoByKey(self, r, key):
        v = None
        for body in r['body']:
            try:
                v = body['data'][0][key]
            except:
                pass
        return v

    def __getRaidBossId(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "cnt=14e64896ccb&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
            }
        post_url = "http://v272.cc.mobimon.com.tw/raid/list?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        #self.logger.debug("Raw data = {0}".format(r))
        try:
            # bossCount = len(r['body'][0]['data'])
            # self.logger.debug("Boss Count = {0}".format(bossCount))
            for r in r['body'][0]['data']:
                # self.logger.debug(u"魔神戰資訊 = {0}".format(r))
                if r['own']:
                    self.logger.debug(u"魔神來襲！魔神等級: [{0}]".format(r['boss_param']['lv']))
                    return r['boss_id']
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
                    self.logger.debug(u"發現的魔神已結束")
                    self.__getRaidResult(bossId)
                    self.__getRaidBonus(bossId)
                elif r['res'] == 608:
                    self.logger.error(u"魔神戰逾時")
                    self.__getRaidResult(bossId)
                    self.__getRaidBonus(bossId)
                else:
                    self.logger.error("Unknown Error: {0}".format(r['res']))
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
        post_url = "http://v272.cc.mobimon.com.tw/raid/entry?bid={0}&use=1&fid=1913206&pt=0&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
        payload = "nature=bid%3d{0}%26cnt%3d{1}%26fid%3d1913206%26pt%3d0%26use%3d1".format(bossId, hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug("Get Raid Request result = {0}".format(r['res']))
        return r

    def __getRaidResult(self, bossId):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "bid={0}&cnt={1}&damage=994500&mission=%7b%22cid%22%3a%5b1032%2c57%2c7505%2c3022%2c1021%2c38%5d%2c%22fid%22%3a43%2c%22ms%22%3a0%2c%22md%22%3a149140%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a1%2c%22fw%22%3a3%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bid%3d{0}%26cnt%3d{1}%26damage%3d994500%26mission%3d%257b%2522cid%2522%253a%255b1032%252c57%252c7505%252c3022%252c1021%252c38%255d%252c%2522fid%2522%253a43%252c%2522ms%2522%253a0%252c%2522md%2522%253a149140%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%252c%25225%2522%253a1%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a1%252c%2522fw%2522%253a3%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26res%3d1%26t%3d15&res=1&t=15&timestamp={2}".format(bossId, hexNow, now)
            }
        post_url = "http://v272.cc.mobimon.com.tw/raid/result?bid={0}&res=1&damage=9994500&t=15&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
        payload = "mission=%7b%22cid%22%3a%5b1032%2c57%2c7505%2c3022%2c1021%2c38%5d%2c%22fid%22%3a43%2c%22ms%22%3a0%2c%22md%22%3a198601%2c%22sc%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%2c%224%22%3a0%7d%2c%22es%22%3a0%2c%22at%22%3a0%2c%22he%22%3a0%2c%22da%22%3a0%2c%22ba%22%3a0%2c%22bu%22%3a0%2c%22job%22%3a%7b%220%22%3a3%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a0%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a1%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a0%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a0%2c%222%22%3a0%2c%223%22%3a0%7d%2c%22fj%22%3a1%2c%22fw%22%3a3%2c%22fo%22%3a0%2c%22cc%22%3a1%7d&nature=bid%3d{0}%26cnt%3d{1}%26damage%3d994500%26mission%3d%257b%2522cid%2522%253a%255b1032%252c57%252c7505%252c3022%252c1021%252c38%255d%252c%2522fid%2522%253a43%252c%2522ms%2522%253a0%252c%2522md%2522%253a198601%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a3%252c%25221%2522%253a1%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a0%252c%25222%2522%253a1%252c%25223%2522%253a1%252c%25224%2522%253a1%252c%25225%2522%253a1%252c%25228%2522%253a1%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a1%252c%2522fw%2522%253a3%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26res%3d1%26t%3d15".format(bossId, hexNow)
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
        post_url = "http://v272.cc.mobimon.com.tw/raid/record?bid={0}&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
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
        post_url = "http://v272.cc.mobimon.com.tw/user/recover_ap?type=1&item_id=1&cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}%26item_id%3d1%26type%3d1".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        if r['res'] == 0:
            self.logger.warning("體力完全回復")
        elif r['res'] == 703:
            self.logger.warning("體力果實不足，無法回復體力")
        else:
            self.logger.error("體力無法回復, Error Code:{0}".format(r['res']))
            sys.exit(0)
        return r

    def __initLogger(self, tail_name=None):
        fileFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        # consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            # ' - %(message)s', datefmt='%B %d %H:%M:%S')

        self.logger = logging.getLogger("Chain Chronicle")
        self.logger.setLevel(logging.DEBUG)

        log_name = "cc_{0}.log".format(tail_name)
        rh = RotatingFileHandler(log_name, maxBytes=1024*10000, backupCount=5)
        rh.setLevel(logging.DEBUG)
        rh.setFormatter(fileFormatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(consoleFormatter)

        self.logger.addHandler(rh)
        self.logger.addHandler(console)

    def get_item_from_storage(self):
        idx=154619903
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "cnt={0}&nature=cnt%3d{0}%26p%3d{2}&p={2}&timestamp={1}".format(hexNow, now, idx)
                    }
        post_url = "http://v272.cc.mobimon.com.tw/present/recv?p={0}&cnt={1}&timestamp={2}".format(idx, hexNow, now)
        payload = "nature=cnt%3d{0}%26p%3d{1}".format(hexNow, idx)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug(r)
        return r

    def CC_ClearItems(self, max_sell_count):
        all_data = self.CC_GetAllData()
        cards = all_data['body'][6]['data']
        count = 0
        idx = 0
        while(count < max_sell_count):
            print idx
            c = cards[idx]
            idx += 1
            # self.logger.debug("Now Trying to sell item {0}".format(c['id']))
            time.sleep(0.1)
            # self.logger.debug()
            # print count
            # print c['idx']
            if 'type' in c and c['type'] in [2, 3]:
                self.logger.debug(u"賣出物品 {0}".format(c['id']))
                r = self.__sellItem(c['idx'])
                count += 1
            elif 'type' in c and c['type'] == 0 and 'maxlv' in c and c['maxlv'] >= 70:
                continue
            elif 'locked' in c and c['locked']:
                self.logger.debug(u"聖靈幣鎖住，無法販賣")
                continue
            else:
                self.logger.debug(u"非可販售類別")
                continue
        all_data = self.CC_GetAllData()
        size = len(all_data['body'][6]['data'])
        self.logger.debug("目前包包物品數量 = {0}".format(size))
            # if c['type'] == 2 or c['type'] == 3:
                # r = cc.sellItem(c['idx'])
                # if r['res'] == 0:
                #     print "sell success"
                # else:
                #     print "sell failed"
                #     sys.exit(0)
            # else:
            #     continue

    def CC_GetLatestCharInfo(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "cnt={0}&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
            }
        post_url = "http://v272.cc.mobimon.com.tw/data/charainfo?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug(r)
        return r


    def find_best_idx_to_explorer(self, area, area_pickup_list, except_card_idx=[]):
        # for pickup in pickup_list:
            # self.logger.debug(pickup)
        card_list = self.CC_GetAllData()['body'][6]['data']
        self.logger.debug("Pickup attribute home: {0}".format(area_pickup_list['home']))
        self.logger.debug("Pickup attribute job type: {0}".format(area_pickup_list['jobtype']))
        self.logger.debug("Pickup attribute weapontype: {0}".format(area_pickup_list['weapontype']))
        for card in card_list:
            if card['type'] == 0:
                temp_idx = card['idx']
                temp_id = card['id']
                card_doc = self.db.charainfo.find_one({"cid": card['id']})
                if card_doc:
                    # self.logger.debug("home:{0}, {1}".format(card_doc['home'], type(card_doc['home'])))
                    # self.logger.debug("jobtype:{0}".format(card_doc['jobtype']))
                    # TODO: bug here, weapon type is not equal to battletype, how to solve it due to mongodb has no weapon type record
                    # self.logger.debug("weapontype:{0}".format(card_doc['battletype']))
                    if (int(area_pickup_list['home']) == card_doc['home']) or (int(area_pickup_list['jobtype']) == card_doc['jobtype']) or (int(area_pickup_list['weapontype']) == card_doc['battletype']):
                            temp_idx = card['idx']
                            if temp_id in except_card_idx:
                                continue
                            if card_doc['rarity'] == 5:
                                continue
                            self.logger.debug(u"Found pickup card! {0}".format(card_doc['name']))
                            self.logger.debug("{0} is picked to eplorer".format(temp_idx))
                            return temp_idx
                    else:
                        continue
                else:
                    continue

                self.logger.error("Cannot find card id {0} in database, please update DB".format(card['id']))
                self.logger.debug("{0} is picked to eplorer".format(temp_idx))
            else:
                continue
        return temp_idx

    def CC_get_daily_gacha_ticket_thread_wrapper(self):
        while True:
            item = q.get()
            # print "get data: {0}".format(item)
            self.CC_get_daily_gacha_ticket()
            q.task_done()

    def CC_get_daily_gacha_ticket(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
            'Cookie': 'sid={0}'.format(self.sid),
            'nat': "cnt={0}&id=7&kind=limit_item&limit_id=9000&nature=cnt%3d{0}%26id%3d7%26kind%3dlimit_item%26limit_id%3d9000%26price%3d25%26type%3ditem%26val%3d1&price=25&timestamp={1}&type=item&val=1".format(hexNow, now)
            }
        post_url = "http://v272.cc.mobimon.com.tw/token?kind=limit_item&limit_id=9000&type=item&id=7&val=1&price=25&cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}%26id%3d7%26kind%3dlimit_item%26limit_id%3d9000%26price%3d25%26type%3ditem%26val%3d1".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug(r)
        return r

    def CC_TotalWar(self, tid, ring=0, sell=1):
        # accept total war
        self.logger.debug(u"Accept TotalWar")
        url = 'http://v272.cc.mobimon.com.tw/totalwar/accept'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {
            'ring': ring
        }
        ret = self.poster.post_data(url, headers, cookies, **data)

        # get total war
        self.logger.debug(u"Start total war")
        ret = self.__start_total_war(tid)
        # self.logger.debug(ret)

        # finish total war
        self.logger.debug(u"Finish Total war")
        ret = self.__finish_total_war(tid, sell)
        # self.logger.debug(ret)

    def __start_total_war(self, tid):
        fid = 1683830
        url = 'http://v272.cc.mobimon.com.tw/totalwar/entry'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {
            'tid': tid,
            'fid': fid,
            'pt': 0
        }
        r = self.poster.post_data(url, headers, cookies, **data)
        return r

    def __finish_total_war(self, tid, sell):
        url = 'http://v272.cc.mobimon.com.tw/totalwar/result'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {
            'res': 1,
            'tid': tid
        }
        r = self.poster.post_data(url, headers, cookies, **data)
        # self.logger.debug(r)

        if sell:
            try:
                for earn in r['body'][1]['data']:
                    # id = earn['id']
                    idx = earn['idx']
                    # self.logger.debug(idx)
                    r = self.__sellItem(idx)
                    if r['res'] == 0:
                        self.logger.debug(u"\t-> 賣出卡片 {0}, result = {1}".format(idx, r['res']))
                    else:
                        self.logger.error(u"\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
                        sys.exit(0)
            except Exception as e:
                self.logger.warning(u"無可販賣卡片")
        return r

    def CC_GetPresents(self, sell=False):
        # Get present list
        # self.logger.debug(u"Get present id")
        url = 'http://v272.cc.mobimon.com.tw/present/list'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}
        data = {}
        ret = self.poster.post_data(url, headers, cookies, **data)
        present_ids = [data['idx'] for data in ret['body'][0]['data']]
        self.logger.debug("Present count = {0}".format(len(present_ids)))
        # self.logger.debug("Present ids = {0}".format(present_ids))

        # Get present
        url = 'http://v272.cc.mobimon.com.tw/present/recv'
        cookies = {'sid': self.sid}
        headers = {'Cookie': 'sid={0}'.format(self.sid)}

        while len(present_ids) > 0:
            pid = present_ids.pop(0)
            self.logger.debug("Get item: {0}".format(pid))
            data = {'p': pid}
            ret = self.poster.post_data(url, headers, cookies, **data)
            if sell is True:
                self.__sellItem(pid)
        return ret


if __name__ == "__main__":

    action = None
    if len(sys.argv) < 4:
        print "Usage: python %s setting.ini -action {quest | gacha | buy}" %sys.argv[0]
        sys.exit(0)
    else:
        configFile = sys.argv[1]
        if sys.argv[2] == "-action":
            action = sys.argv[3]

    cc = ChainChronicleAutomation(configFile)
    config = cc.getConfigDictionary()
    logger = cc.getLogger()
    cc.CC_Login()
    print "complete login"
    if action == 'gacha':
        count = config['Gacha']['count']
        bSell = config['Gacha']['sell']
        gType = config['Gacha']['type']
        keptCards = None
        if config['Gacha']['keep_cards']:
            keptCards = [ int(n) for n in config['Gacha']['keep_cards'].split(',') ]
        cc.CC_Gacha(gType, count, bSell, keptCards)
    elif action == 'password':
        cc.CC_SetPassword('aaa123')
    elif action == 'sell':
        cc.CC_ClearItems(700)
    elif action == 'quest':
        now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        logger.info("#Start at: {0}".format(now))
        quest_list = config['Quest']['quest_id'].split(';')
        count = config['Quest']['count']
        bRaid = config['Quest']['raid']
        bSell = config['Quest']['sell']
        maxEventPoint = config['Quest']['max_event_point']
        if maxEventPoint == -1:
            maxEventPoint = sys.maxint

        for quest in quest_list:
            if not quest:
                continue
            quest_info = quest.split(',')
            qtype = quest_info[0]
            qid = quest_info[1]
            if len(quest_info) == 3:
                count = int(quest_info[2])
            # print qtype
            # print qid
            try:
                cc.CC_PlayQuest(qtype, qid, count, bRaid, bSell, maxEventPoint)
            except Exception as e:
                raise
                logger.info(e)
                continue
            now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            logger.info("#End at: {0}".format(now))
            time.sleep(1)
    elif action == 'buy':
        count = config['Buy']['count']
        cc.CC_buyStaminaFruit(count)
    elif action == 'buy_item':
        item_type = config['Buy']['type']
        count = config['Buy']['count']
        cc.CC_buyItem(item_type, count)
    elif action == 'list_latest':
        r = cc.CC_GetLatestCharInfo()
        logger.debug(json.dumps(r))

    elif action == 'explorer_cancel':
        for i in range(1, 4):
            cc.cc.CC_explorer_cancel(i)

    elif action == 'explorer':
        # r = cc.get_item_from_storage()
        # money_goal = 500000000

        # money_current = 99999999999999
        # while True:
        r = cc.CC_explorer_get_pickup()
        if r['res'] != 0:
            logger.error("無法取得探索資訊")
            sys.exit(0)
        else:
            pickup_list = r['pickup']


        # area = config['Explorer']['area']
        # card_idx = config['Explorer']['card_idx']
        # interval = config['Explorer']['interval']

        if config['Explorer']['area']:
            area_list = [ int(n) for n in config['Explorer']['area'].split(',') ]

        # if config['Explorer']['card_idx']:
        #     card_idx_list = [ int(n) for n in config['Explorer']['card_idx'].split(',') ]

        # if config['Explorer']['interval']:
        #     interval_list = [ int(n) for n in config['Explorer']['interval'].split(',') ]
        # 菲娜，主角x2
        except_card_idx = [7017, 7024, 7015, 51]
        for i in range(0, 3):
            # get result
            while True:
                r = cc.CC_explorer_result(i+1)
                # No explorer data or get result success
                if r['res'] == 2308 or r['res'] == 0:
                    break
                elif r['res'] == 2302:
                    logger.warning(u"探索尚未結束..稍後重試")
                    time.sleep(60)
                else:
                    logger.warning("未知的探索結果")
                    logger.warning(r)
                    break

            area = area_list[i]
            card_idx = cc.find_best_idx_to_explorer(area, pickup_list[area], except_card_idx)
            except_card_idx.append(card_idx)
            # interval = interval_list[i]


            # go to explorer
            r = cc.CC_explorer(i+1, area, card_idx)

            # r = cc.CC_explorer_cancel(1)

            # if reulst != 0:
            #     logger.debug(r)
            #     # pick retry
            #     logger.warning("Pickup error, try another pickup value")
            #     r = cc.CC_explorer(i+1, area, card_idx, 1)
            #     logger.debug(r)
                # r = cc.CC_explorer_cancel(1)

            # this function can be used to consume money to avoid money overflow
            # if i % 5000 == 0:
            #     r = cc.CC_GetAllData()
            #     data = r['body'][8]['data']
            #     for d in data:
            #         if d['item_id'] == 10:
            #             if d['cnt'] <= 1000000000:
            #                 sys.exit(0)
            #             logger.info(u"剩餘金幣 = {0}".format(d['cnt']))
            #             money_current = d['cnt']
            #             break

    elif action == 'status':
        r = cc.CC_GetAllData()
        item_mapping = {
            #2: '魂力果實',
            #3: '復活果實',
            #5: '超魂力果實',
            7: '轉蛋卷',
            10: "金幣",
            11: '聖靈幣',
            13: '戒指',
            15: '賭場幣',
            20: '轉蛋幣',
        }

        data_list = r['body'][8]['data']
        #logger.info(json.dumps(data_list, sort_keys=True, indent=2))
        for data in data_list:
            try:
                logger.debug("{0} = {1}".format(item_mapping[data['item_id']], data['cnt']))
            except:
                pass
        #logger.info(json.dumps(r, sort_keys=True, indent=2))
    elif action =='subjugation':
        r = cc.CC_Subjugation(5)

    elif action =='totalwar':
        max_count = 800
        for i in xrange(0, max_count):
            logger.debug(u"{0}/{1} 委托".format(i, max_count))
            r = cc.CC_TotalWar(11, ring=1)

    elif action =='poc':
        q = Queue(maxsize=0)
        num_threads = 10
        for i in range(num_threads):
            worker = Thread(target=cc.CC_get_daily_gacha_ticket_thread_wrapper)
            worker.setDaemon(True)
            worker.start()

        for i in range(0, num_threads + 1):
            q.put(i)
        q.join()
    elif action == 'present':
        r = cc.CC_GetPresents(sell=False)
        # logger.debug(type(r))
        # logger.debug(json.dumps(r['body'][8]['data'], sort_keys=True, indent=2))
    else:
        logger.debug("Unsupported action:[{0}]".format(action))



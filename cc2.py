# -*- coding: utf-8 -*
import json
import requests
import sys
import time
import logging
import datetime
from logging.handlers import RotatingFileHandler
# from pymongo import MongoClient
import ConfigParser
from random import randint
import threading

class ChainChronicleAutomation():
    def __init__(self, configFile):
        #self.config['General']['uid'] = "ANDO4779bf78-f0f7-4a16-8d41-3c0d9ab46e0c"
        #self.config['General']['token'] = "APA91bEAKkkmD_eJ07r_NjRMRKJ2keH1A1Ju8mC2MDd9Iu9Bogxoy-HBl8SlCJJmMEM-aCMxnMEDNr-AC5TIiKmUHGRkk-lO1ypSdZhE8PhlQLjvBub3t81kwwwxIDQPw6CsarSI_BJ8"
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
        # self.cardTypes = {0: "角色卡", 1: "武器卡", 2: "鍛造卡", 3: "成長卡"}
        self.cardTypeMapping = {"grwoth":[{"name": u"成長卡"}, {"cid": [90010,90011,90012,90013,90014]}],
                                "weapon":[{"name": u"武器卡"}, {"cid": [93006,93007,93008,93009, 93010, 93011,93021,93022,93023]}],
            }
        self.__initDb()
        self.__loadConfig(configFile)

    def __initDb(self):
        pass
        # client = MongoClient('lineage.twbbs.org', 27017)
        # client = MongoClient('54.64.174.97', 27017)
        # client = MongoClient('127.0.0.1', 27017)


        #client.the_database.authenticate('admin', 'mong730520', source = 'admin')
        # self.db = client.cc

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


            self.config['Buy']['count'] = config.getint('Buy', 'Count')
            self.config['Buy']['type'] = config.get('Buy', 'Type')
            try:
                self.config['General']['RetryDurtion'] = config.getint('General', 'RetryDuration')
            except:
                self.config['General']['RetryDurtion'] = 10

            try:
                self.config['Explorer']['area'] = config.getint('Explorer', 'area')
            except:
                self.config['Explorer']['area'] = 0

            try:
                self.config['Explorer']['card_idx'] = config.getint('Explorer', 'card_idx')
            except:
                self.config['Explorer']['card_idx'] = 0

            try:
                self.config['Explorer']['interval'] = config.getint('Explorer', 'interval')
            except:
                self.config['Explorer']['interval'] = 0

            # for key in self.config:
            #    self.logger.debug('Key = {0}, Value = {1}'.format(key, self.config[key]))
        except Exception as e:
            raise
            sys.exit(0)

    def getConfigDictionary(self):
        return self.config

    def getLogger(self):
        return self.logger

    def CC_GetAllData(self):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "cnt=14e5c7f82a4&nature=c%3d1%26cnt%3d{0}%26t%3d6&t=6&timestamp={1}".format(hexNow, now)
                    }
        post_url = "http://ios5.cc.mobimon.com.tw/user/all_data?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}%26t%3d6".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        return r

    def CC_Login(self):
        # Login and get sid
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': 'INVALID'}
        self.headers = {
                'Cookie': 'sid=INVALID',
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436052183%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.config['General']['uid'], self.config['General']['token'])
                }
        post_url = "http://prod4.cc.mobimon.com.tw/session/login?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%22{1}%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d".format(hexNow, int(time.time()), self.config['General']['uid'], self.config['General']['token'])
        r = requests.post(post_url, data=payload, headers=self.headers)
        # self.logger.debug(r)
        try:
            self.sid = r.json()['login']['sid']
            #all_data = self.CC_GetAllData()
            #rings = all_data['body'][8]['data'][9]
            #self.logger.debug("ring: {0}".format(rings))
            #self.logger.debug("ChainChronicle Login result = [{0}]".format(r.json()['res']))
            #self.logger.debug("session ID = {0}".format(self.sid))
        except Exception as e:
            self.logger.error("無法登入, Message = {0}".format(r.json()['msg']))
            sys.exit(0)

    def CC_PlayQuest(self, qtype, qid, count, bRaid, bSell, maxEventPoint):
        #for i in range(0, count):
        current = 0
        bInfinte = False

        if count == -1:
            bInfinte = True

        while True:
            current = current + 1
            if current > count and not bInfinte:
                break
            #print "Start to play quest:[{0}]".format(i)
            result = self.__getQuest(qtype, qid).json()
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
			self.CC_Gacha(6, 15, 1, None)
                time.sleep(1)
                current = current - 1
                continue
            if self.config['General']['Delay'] > 0:
                # self.logger.debug(self.config['General']['Delay'])
                random_salt = randint(0,99)
                # random 0 ~ 99 second
                sleep_in_sec = 60 * self.config['General']['Delay'] + random_salt
                self.logger.info("等待{0}秒後完成戰鬥...".format(sleep_in_sec))
                time.sleep(sleep_in_sec)
            result = self.__getBattleResult(qid).json()
            if result['res'] == 0:
                self.logger.info(u"#{0} - 戰鬥完成!".format(current))
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
                return

            #魔神戰
            self.__PlayRaid(bRaid)

            time.sleep(1)

    def CC_SetPassword(self, password):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}&timestamp={1}".format(hexNow, now)
                }
        post_url = "http://prod4.cc.mobimon.com.tw/user/get_account?cnt={0}&timestamp={1}".format(hexNow, now)
        payload = "nature=cnt%3d{0}".format(hexNow)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug(r)

        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}%26pass%3d{2}&pass={2}&timestamp={1}".format(hexNow, now, password)
                }
        post_url = "http://prod4.cc.mobimon.com.tw/user/set_password?cnt={0}&timestamp={1}".format(hexNow, now)
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
            post_url = "http://prod4.cc.mobimon.com.tw/gacha?t={2}&c={3}&cnt={0}&timestamp={1}".format(hexNow, now, gType, batchCount)
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
                    self.logger.error("Key Error:{0}, 找不到卡片idx, 可能是包包已滿".format(e))
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
            self.logger.debug("#{0} 購買道具".format(i+1))
            now = int(time.time()*1000)
            hexNow = format(now + 5000, 'x')
            cookies = {'sid': self.sid}
            self.headers = {
                    'Cookie': 'sid={0}'.format(self.sid),
                    'nat': "cnt={0}&id={2}&kind=item&nature=cnt%3d{0}%26id%3d{2}%26kind%3ditem%26price%3d30%26type%3d{3}%26val%3d1&price=30&timestamp={1}&type={3}&val=1".format(hexNow, now, item_mapping[item_type]['id'], item_mapping[item_type]['type'])
                    }
            post_url = "http://v252.cc.mobimon.com.tw/token?kind=item&type={2}&id={3}&val={4}&price={5}&cnt={0}&timestamp={1}".format(hexNow, now, item_mapping[item_type]['type'], item_mapping[item_type]['id'], item_mapping[item_type]['val'], item_mapping[item_type]['price'])
            payload = "nature=cnt%3d{0}%26id%3d{1}%26kind%3ditem%26price%3d{2}%26type%3d{3}%26val%3d{4}".format(hexNow, item_mapping[item_type]['id'], item_mapping[item_type]['price'], item_mapping[item_type]['type'], item_mapping[item_type]['val'])
            r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
            #self.logger.debug(post_url)
            #self.logger.debug(payload)
            #self.logger.debug(self.headers)
            if(r['res']!=0):
                self.logger.warning("購買角色成長卡失敗, ErrorCode = {0}".format(r['res']))
                return r
            else:
                self.logger.debug("\t-> 完成")
        return r

    def CC_buyStaminaFruit(self, count):
        r = None
        for i in range(0, count):
            self.logger.debug("#{0} 購買體力果實".format(i+1))
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
            if(r['res']!=0):
                self.logger.warning("購買體力果實失敗, ErrorCode = {0}".format(r['res']))
                return r
            else:
                self.logger.debug("\t-> 完成")
        return r

    def CC_explorer(self, explorer_idx, area, idx, pickup=0):
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
                'nat': "card_idx={2}&cnt={0}&explorer_idx={6}&helper1={3}&helper2={4}&interval=2&"\
                "location_id={5}&nature=card_idx%3d{2}%26cnt%3d{0}%26explorer_idx%3d1%26helper1%3d{3}%26helper2%3d{4}%26"\
                "interval%3d2%26location_id%3d{5}%26pickup%3d{7}&pickup={7}&timestamp={1}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)
                }
        post_url = "http://v252.cc.mobimon.com.tw/explorer/entry?explorer_idx={6}&location_id={5}&card_idx={2}&pickup" \
        "={7}&interval=2&helper1={3}&helper2={4}&cnt={0}&timestamp={1}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)

        payload = "nature=card_idx%3d{2}%26cnt%3d{0}%26explorer_idx%3d{6}%26helper1%3d{3}%26helper2%3d{4}%26interval%3d2%26location_id%3d{5}%26pickup%3d{7}".format(hexNow, now, idx, helper1, helper2, area, explorer_idx, pickup)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug(json.dumps(r))
        # self.logger.debug(json.dumps(r['res']))
        return r['res']

    def CC_explorer_cancel(self, explorer_idx):
        now = int(time.time()*1000)
        hexNow = format(now + 5000, 'x')
        cookies = {'sid': self.sid}
        # explorer_idx = "1"
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&explorer_idx={2}&nature=cnt%3d{0}%26explorer_idx%3d{2}&timestamp={1}".format(hexNow, now, explorer_idx)
                }
        post_url = "http://v252.cc.mobimon.com.tw/explorer/cancel?explorer_idx={2}&cnt={0}&timestamp={1}".format(hexNow, now, explorer_idx)

        payload = "nature=cnt%3d{0}%26explorer_idx%3d{2}".format(hexNow, now, explorer_idx)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        # self.logger.debug(json.dumps(r))
        return r


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
        return r


    def __getQuest(self, qtype, qid):
        # Get Quest
        now = int(time.time())
        hexNow = format(now+5000, 'x')
        cookies = {'sid': self.sid}
        self.headers = {
                'Cookie': 'sid={0}'.format(self.sid),
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436043943%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436043943%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.config['General']['uid'], self.config['General']['token'])
                }
        post_url = "http://prod4.cc.mobimon.com.tw/quest/entry?oc=1&type={3}&qid={0}&fid=198601&pt=0&cnt={1}&timestamp={2}".format(qid, hexNow, now, qtype)
        payload = "nature=cnt%3d{0}%26fid%3d198601%26pt%3d0%26qid%3d{2}%26type%3d{1}".format(hexNow, qtype, qid)
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
                'nat': "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436043943%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522{2}%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522{3}%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436043943%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1851%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}".format(hexNow, now, self.config['General']['uid'], self.config['General']['token'])
                }
        post_url = "http://prod4.cc.mobimon.com.tw/quest/result?qid={0}&res=1&bt=1200&time=0.00&d=1&s=1&cc=1&wc=5&wn=5&cnt={1}&timestamp={2}".format(qid, hexNow, now)
        payload = "ch=&eh=&ec=&mission=%7b%22cid%22%3a%5b7505%2c5033%2c52%2c38%2c7502%2c45%5d%2c%22fid%22%3a198601%2c%22ms%22%3a1%2c%22md%22%3a200001%2c%22sc%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a0%7d%2c%22es%22%3a1%2c%22at%22%3a1%2c%22he%22%3a1%2c%22da%22%3a1%2c%22ba%22%3a1%2c%22bu%22%3a1%2c%22job%22%3a%7b%220%22%3a1%2c%221%22%3a1%2c%222%22%3a2%2c%223%22%3a1%2c%224%22%3a2%7d%2c%22weapon%22%3a%7b%220%22%3a2%2c%221%22%3a1%2c%222%22%3a1%2c%223%22%3a1%2c%224%22%3a2%2c%225%22%3a1%2c%228%22%3a1%2c%229%22%3a1%2c%2210%22%3a0%7d%2c%22box%22%3a1%2c%22um%22%3a%7b%221%22%3a1%2c%222%22%3a1%2c%223%22%3a0%7d%2c%22fj%22%3a-1%2c%22fw%22%3a-1%2c%22fo%22%3a1%2c%22cc%22%3a1%7d&nature=bt%3d1200%26cc%3d1%26ch%3d%26cnt%3d{0}%26d%3d1%26ec%3d%26eh%3d%26mission%3d%257b%2522cid%2522%253a%255b7505%252c5033%252c52%252c38%252c7502%252c45%255d%252c%2522fid%2522%253a198601%252c%2522ms%2522%253a0%252c%2522md%2522%253a200000%252c%2522sc%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%252c%25224%2522%253a0%257d%252c%2522es%2522%253a0%252c%2522at%2522%253a0%252c%2522he%2522%253a0%252c%2522da%2522%253a0%252c%2522ba%2522%253a0%252c%2522bu%2522%253a0%252c%2522job%2522%253a%257b%25220%2522%253a1%252c%25221%2522%253a1%252c%25222%2522%253a2%252c%25223%2522%253a1%252c%25224%2522%253a2%257d%252c%2522weapon%2522%253a%257b%25220%2522%253a2%252c%25221%2522%253a1%252c%25222%2522%253a0%252c%25223%2522%253a1%252c%25224%2522%253a2%252c%25225%2522%253a1%252c%25228%2522%253a0%252c%25229%2522%253a0%252c%252210%2522%253a0%257d%252c%2522box%2522%253a1%252c%2522um%2522%253a%257b%25221%2522%253a0%252c%25222%2522%253a0%252c%25223%2522%253a0%257d%252c%2522fj%2522%253a-1%252c%2522fw%2522%253a-1%252c%2522fo%2522%253a0%252c%2522cc%2522%253a1%257d%26qid%3d220103%26res%3d1%26s%3d0%26time%3d0.00%26wc%3d5%26wn%3d5".format(hexNow)

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
        post_url = "http://prod4.cc.mobimon.com.tw/raid/list?cnt={0}&timestamp={1}".format(hexNow, now)
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
        post_url = "http://prod4.cc.mobimon.com.tw/raid/entry?bid={0}&use=1&fid=1913206&pt=0&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
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
        post_url = "http://prod4.cc.mobimon.com.tw/raid/result?bid={0}&res=1&damage=9994500&t=15&cnt={1}&timestamp={2}".format(bossId, hexNow, now)
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
            self.logger.warning("體力完全回復")
        elif r['res'] == 703:
            self.logger.warning("體力果實不足，無法回復體力")
        else:
            self.logger.error("體力無法回復, Error Code:{0}".format(r['res']))
            sys.exit(0)
        return r

    def __initLogger(self):
        fileFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        # consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
            # ' - %(message)s', datefmt='%B %d %H:%M:%S')

        self.logger = logging.getLogger("Chain Chronicle")
        self.logger.setLevel(logging.DEBUG)

        rh = RotatingFileHandler("cc.log", maxBytes=10240*3, backupCount=3)
        rh.setLevel(logging.INFO)
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
        post_url = "http://prod4.cc.mobimon.com.tw/present/recv?p={0}&cnt={1}&timestamp={2}".format(idx, hexNow, now)
        payload = "nature=cnt%3d{0}%26p%3d{1}".format(hexNow, idx)
        r = requests.post(post_url, data=payload, headers=self.headers, cookies=cookies).json()
        self.logger.debug(r)
        return r

    def CC_ClearItems(self, max_sell_count):
        all_data = self.CC_GetAllData()
        cards = all_data['body'][6]['data']
        # self.logger.debug(cards)
        count = 0
        idx = 0
        while(count < max_sell_count):
            c = cards[idx]
            idx += 1
            # self.logger.debug("Now Trying to sell item {0}".format(c['id']))
            time.sleep(0.1)
            # self.logger.debug()
            # print count
            # print c['idx']
            if 'locked' in c and c['locked']:
                self.logger.debug("聖靈幣鎖住，無法販賣")
                continue
            else:
                self.logger.debug("賣出物品 {0}".format(c['id']))
                r = self.__sellItem(c['idx'])
                count += 1
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


    if action == 'gacha':
        count = config['Gacha']['count']
        bSell = config['Gacha']['sell']
        gType = config['Gacha']['type']
        keptCards = None
        if config['Gacha']['keep_cards']:
            keptCards = [ int(n) for n in config['Gacha']['keep_cards'].split(',') ]

        # for i in range(1, 3):
        #    threading.Thread(target = cc.CC_Gacha, args = (gType, count, bSell, keptCards), name =  'thread-'  + str(i)).start()
        cc.CC_Gacha(gType, count, bSell, keptCards)
    # elif action == 'raid_gacha':
    #     count = config['RaidGacha']['count']
    #     bSell = config['RaidGacha']['sell']
    #     keepCardId = config['RaidGacha']['keepCardId']
    #     cc.CC_RaidGacha(count, bSell, keepCardId)
    elif action == 'password':
        cc.CC_SetPassword('aaa123')
    elif action == 'sell':
        cc.CC_ClearItems(10)
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
            qtype = quest.split(',')[0]
            qid = quest.split(',')[1]
            # print qtype
            # print qid
            try:
                cc.CC_PlayQuest(qtype, qid, count, bRaid, bSell, maxEventPoint)
            except Exception as e:
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
        cc.CC_buyItem(item_type, 1)
    elif action == 'explorer':
        # r = cc.get_item_from_storage()
        # money_goal = 500000000

        # money_current = 99999999999999
        # while True:
        area = config['Explorer']['area']
        card_idx = config['Explorer']['card_idx']
        interval = config['Explorer']['interval']
        for i in range(1, 1300000):

            logger.debug("#{0}".format(i))
            if cc.CC_explorer(1, area, card_idx, 0) != 0:
                # pick retry
                logger.warning("Pickup error, try another pickup value")
                cc.CC_explorer(1, area, card_idx, 1)
            r = cc.CC_explorer_cancel(1)

            if i % 500 == 0:
                r = cc.CC_GetAllData()
                data = r['body'][8]['data']
                for d in data:
                    if d['item_id'] == 10:
                        logger.debug(u"剩餘金幣 = {0}".format(d['cnt']))
                        money_current = d['cnt']
                        break

    elif action == 'status':
        r = cc.CC_GetAllData()
        #logger.debug(type(r))
        logger.debug(json.dumps(r['body'][8]['data'], sort_keys=True, indent=2))
    else:
        logger.debug("Unsupported action:[{0}]".format(action))



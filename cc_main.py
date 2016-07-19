# -*- coding: utf-8 -*
import argparse
import os
import utils.cc_logger
import utils.enhanced_config_parser
import utils.poster
import quest_client
import recovery_client
import item_client
import gacha_client
import time
import urllib
import simplejson
from random import randint
import sys


class ChainChronicle(object):

    def __init__(self, c):
        if os.path.isfile(c):
            self.config_file = c
        else:
            raise IOError("{0} is not exist".format(c))

        self.poster = utils.poster.Poster

        self.action_list = list()
        self.account_info = dict()
        log_id = os.path.basename(os.path.splitext(self.config_file)[0])
        self.__init_logger(log_id)
        self.config = utils.enhanced_config_parser.EnhancedConfigParser()
        self.action_mapping = {
            'QUEST': self.do_quest_section,
            'GACHA': self.do_gacha_section,
            'BUY': self.do_buy_item_section
        }

    def __init_logger(self, log_id):
        self.logger = utils.cc_logger.CCLogger.get_logger(log_id)

    def load_config(self):
        self.config.read(self.config_file)
        for section in self.config.sections():
            if section == utils.enhanced_config_parser.EnhancedConfigParser.SEC_GLOBAL:
                continue
            else:
                if section == 'GENERAL':
                    self.action_list = self.config.getlist(section, 'Flow')
                    self.account_info['uid'] = self.config.get(section, 'Uid')
                    self.account_info['token'] = self.config.get(section, 'Token')

    def start(self):
        self.do_login()
        for action in self.action_list:
            self.do_action(action)

    def do_action(self, action_name):
        for action, action_function in self.action_mapping.iteritems():
            if action in action_name:
                action_function(action_name)

    def do_login(self):
        url = 'http://prod4.cc.mobimon.com.tw/session/login'
        headers = {'Cookie': 'sid=INVALID'}
        data = {
            'UserUniqueID': self.account_info['uid'],
            'Token': self.account_info['token']
        }
        payload_dict = {
          "APP": {
            "time": time.time()
          },
          "DEV": data
        }
        payload = 'param=' + urllib.quote_plus(simplejson.dumps(payload_dict))
        ret = self.poster.post_data(url, headers, None, payload, **data)
        self.logger.debug(ret['login']['sid'])
        try:
            self.account_info['sid'] = ret['login']['sid']
        except KeyError:
            msg = "無法登入, Message = {0}".format(ret['msg'])
            self.logger.error(msg)
            raise KeyError(msg)

    def do_quest_section(self, section, *args, **kwargs):
        self.logger.info("Do quest section: {0}".format(section))
        quest_info = dict()
        quest_info['qtype'] = self.config.get(section, 'QuestId').split(',')[0]
        quest_info['qid'] = self.config.get(section, 'QuestId').split(',')[1]
        quest_info['raid'] = self.config.getint(section, 'AutoRaid')
        quest_info['fid'] = 196530
        count = self.config.getint(section, 'Count')
        b_infinite = True if count == -1 else False

        current = 0
        while True:
            current += 1
            if current > count and b_infinite is False:
                break
            self.logger.debug(u"#{0} 開始關卡".format(current))
            result = quest_client.start_quest(quest_info, self.account_info['sid'])
            # self.logger.debug(result)
            if result['res'] == 0:
                # self.logger.debug(u"取得關卡成功")
                pass
            elif result['res'] == 103:
                self.logger.warning(u"AP 不足, 使用體力果")
                self.do_recover_stamina_process()
                current -= 1
                time.sleep(1)
                continue
            else:
                self.logger.error(u"未知的錯誤 = {0}".format(result))

            if self.config.getint('GLOBAL', 'Delay') > 0:
                self.__sleep(self.config.getint('GLOBAL', 'Delay'), salt=True)

            result = quest_client.finish_quest(quest_info, self.account_info['sid'])
            # self.logger.debug("Quest finish result = {0}".format(result['res']))
            if result['res'] == 0:
                self.logger.debug(u"    -> 關卡完成".format(current))
            else:
                self.logger.debug(u"    -> 關卡失敗".format(current))
            time.sleep(1)

    def do_gacha_section(self, section, *args, **kwargs):
        gacha_info = dict()

        gacha_info['count'] = self.config.getint(section, 'Count')
        gacha_info['gacha_type'] = self.config.getint(section, 'Type')

        try:
            gacha_info['auto_sell'] = self.config.getint(section, 'AutoSell')
        except :
            gacha_info['auto_sell'] = 0

        try:
            gacha_info['keep_cards'] = self.config.getlist(section, 'KeepCards')
        except:
            gacha_info['keep_cards'] = list()

        self.do_gacha_process(gacha_info)



    def do_buy_item_section(self, section, *args, **kwargs):
        # ret = item_client.buy_item(data, self.account_info['sid'])
        # return ret
        pass

    def buy_ap_fruit(self):
        data = {
            'kind': 'item',
            'type': 'item',
            'id': 1,
            'val': 1,
            'price': 10,
        }
        ret = item_client.buy_item(data, self.account_info['sid'])
        if ret['res'] == 0:
            self.logger.debug(u"購買體力果實完成")
        else:
            self.logger.debug(u"購買體力果實失敗: {0}".format(ret['res']))
        return ret

    def do_gacha_process(self, gacha_info):
        """Gacha and sell"""
        for i in xrange(0, gacha_info['count']):
            self.logger.info(u"#{0}: 轉蛋開始！".format(i + 1))
            gacha_result = self.do_gacha(gacha_info['gacha_type'])
            self.logger.debug(u"得到卡片: {0}".format(gacha_result.values()))
            if gacha_result is None or len(gacha_result) == 0:
                self.logger.debug("Gacha Error")
                break

            # Auto sell cards and keep some cards
            if gacha_info['auto_sell'] == 1:
                for cidx, cid in gacha_result.iteritems():
                    if cid in gacha_info['keep_cards']:
                        continue
                    else:
                        ret = self.do_sell_item(cidx)
                        if ret['res'] == 0:
                            self.logger.debug(u"賣出卡片成功")
                        else:
                            self.logger.debug(u"賣出卡片失敗")

    def do_recover_stamina_process(self):
        """process for recovery stamina
        1) using AP fruit, if fail do 2)
        2) buy AP friut, if fail do 3)
        3) go to challenge gacha, exchange for rings, and return to quest
        """
        ret = self.do_recover_stamina()
        if ret['res'] == 0:
            self.logger.debug(u"回復 AP 完成")
        elif ret['res'] == 703:
            self.logger.debug(u'回復 AP 失敗')
            self.logger.debug(u'嘗試購買體力果實')
            ret = self.buy_ap_fruit()
            ret['res'] = 1 # mock
            if ret['res'] != 0:
                self.logger.info("開始友情抽換戒")
                gacha_info = {
                    'count': 10,
                    'gacha_type': 6,
                    'auto_sell': 1,
                    'keep_cards': []
                }
                self.do_gacha_process(gacha_info)
        else:
            self.logger.error(u'未知的錯誤，無法回復 AP: {0}'.format(ret))
        return ret['res']

    def do_recover_stamina(self):
        """recovery stamina by using AP fruit"""
        parameter = dict()
        parameter['type'] = 1
        parameter['item_id'] = 1
        ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
        return ret

    def do_gacha(self, g_type):
        gacha_result = {}
        parameter = dict()
        parameter['type'] = g_type
        r = gacha_client.gacha(parameter, self.account_info['sid'])
        # self.logger.debug(r)

        if r['res'] == 0:
            try:
                for record in r['body'][1]['data']:
                    tmp = dict()
                    idx = record['idx']
                    cid = record['id']
                    tmp[idx] = cid
                    gacha_result[idx] = cid
            except KeyError as e:
                self.logger.error(u"Key Error:{0}, 找不到卡片idx, 可能是包包已滿，或是卡片是新的".format(e))
                return gacha_result
            except Exception as e:
                self.logger.error(u"轉蛋完成，但有未知的錯誤: {0}".format(r['res']))
                self.logger.error(r)
                return gacha_result

        elif r['res'] == 703:
            self.logger.error(u"轉蛋失敗，聖靈幣不足")
            return gacha_result
        else:
            self.logger.error(u"轉蛋失敗，未知的錯誤，無法繼續轉蛋:{0}, {1}".format(r['res'], r))
            return gacha_result
        return gacha_result

    def do_sell_item(self, cidx):
        url = 'http://prod4.cc.mobimon.com.tw/card/sell'
        cookies = {'sid': self.account_info['sid']}
        headers = {'Cookie': 'sid={0}'.format(self.account_info['sid'])}
        data = {
            'c': cidx
        }
        r = self.poster.post_data(url, headers, cookies, **data)
        return r

    def __sleep(self, n, salt=False):
        if salt is True:
            random_salt = randint(0, 10)
        else:
            random_salt = 0
        # random 0 ~ 99 second
        sleep_in_sec = 60 * n + random_salt
        self.logger.info("等待{0}秒後完成...".format(sleep_in_sec))
        time.sleep(sleep_in_sec)


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle automation tool")
    parser.add_argument('-c', '--config', help='Config file path', required=True)
    args = parser.parse_args()
    config_file = args.config
    cc = ChainChronicle(config_file)
    cc.load_config()
    cc.start()

if __name__ == '__main__':
    main()


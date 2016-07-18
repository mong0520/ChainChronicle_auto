# -*- coding: utf-8 -*
import argparse
import os
import utils.cc_logger
import utils.enhanced_config_parser
import utils.poster
import quest_client
import time
import urllib
import simplejson
from random import randint


class ChainChronicle():

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
            'QUEST': self.do_quest,
            'GACHA': self.do_gacha,
            'BUY': self.do_buy_item
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

    def do_quest(self, section, *args, **kwargs):
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
            result = quest_client.start_quest(quest_info, self.account_info['sid'])
            # self.logger.debug(result)
            if result['res'] == 103:
                self.logger.warning("體力不足, 使用體力果")
                self.__recover_stamina_process()
                current -= 1
                continue
            else:
                self.logger.debug("Quest entry result = {0}".format(result['res']))
            if self.config.getint('GLOBAL', 'Delay') > 0:
                self.__sleep(self.config.getint('GLOBAL', 'Delay'), salt=True)

            result = quest_client.finish_quest(quest_info, self.account_info['sid'])
            self.logger.debug("Quest finish result = {0}".format(result['res']))


    def do_gacha(self, section, *args, **kwargs):
        print "do gacha"

    def do_buy_item(self, section, *args, **kwargs):
        print "do buy item"

    def __recover_stamina_process(self):
        r = 0  # mock
        # r = self.__recoverStamina()
        if r['res'] != 0:
            self.logger.warning("恢復體力失敗: {0}".format(r['res']))
            self.logger.info("購買體力果實(1)...")
            r = 0  # mock
            # r = self.CC_buyStaminaFruit(1)
            if r['res'] == 0:
                self.logger.debug("購買體力果實完成")
            else:
                self.logger.warning("購買體力果實失敗, result = {0}".format(r['res']))
                self.logger.info("開始友情抽換戒")
                # self.CC_Gacha(6, 20, 1, None)
        time.sleep(1)

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


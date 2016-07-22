# -*- coding: utf-8 -*
import argparse
import os
import sys
import time
import urllib
import simplejson
from random import randint
from lib import explorer_client
from lib import gacha_client
from lib import item_client
from lib import quest_client
from lib import raid_client
from lib import recovery_client
from lib import present_client
from lib import totalwar_client
from lib import alldata_client
import utils.cc_logger
import utils.enhanced_config_parser
import utils.poster
import utils.card_helper


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
            'BUY': self.do_buy_item_section,
            'EXPLORER': self.do_explorer_section,
            'TOTALWAR': self.do_totalwar_section,
            'STATUS':  self.do_show_status,  # no need section in config
            'LIST_CARDS':  self.do_show_all_cards,  # no need section in config
            'DAILY_TICKET': self.do_daily_gacha_ticket  # no need section in config
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
                self.logger.info("### Current Flow = {0} ###".format(action_name))
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
        # self.logger.debug(ret['login']['sid'])
        try:
            self.account_info['sid'] = ret['login']['sid']
        except KeyError:
            msg = "無法登入, Message = {0}".format(ret['msg'])
            self.logger.error(msg)
            raise KeyError(msg)

    def do_daily_gacha_ticket(self, section, *args, **kwargs):
        r = item_client.get_daily_gacha_ticket(self.account_info['sid'])
        self.logger.debug(r)

    def do_show_status(self, section, *args, **kwargs):
        r = alldata_client.get_alldata(self.account_info['sid'])
        item_mapping = {
            # 2: '魂力果實',
            # 3: '復活果實',
            # 5: '超魂力果實',
            7: '轉蛋卷',
            10: "金幣",
            11: '聖靈幣',
            13: '戒指',
            15: '賭場幣',
            20: '轉蛋幣',
        }

        data_list = r['body'][8]['data']
        # logger.info(json.dumps(data_list, sort_keys=True, indent=2))
        for data in data_list:
            try:
                self.logger.debug("{0} = {1}".format(item_mapping[data['item_id']], data['cnt']))
            except KeyError:
                pass

    def do_show_all_cards(self, section, *args, **kwargs):
        """ 只列出四星/五星角色卡 """
        r = alldata_client.get_alldata(self.account_info['sid'])
        card_list = r['body'][6]['data']

        # logger.info(json.dumps(data_list, sort_keys=True, indent=2))
        for card in card_list:
            if card['type'] != 0:  # not character card
                continue
            try:
                cid = int(card['id'])
                card_dict = utils.card_helper.find_card_by_id(cid)
                if card_dict and card_dict['rarity'] >= 4:
                    self.logger.debug(u"{0}, 界限突破：{1}, 等級: {2}, 稀有度: {3}".format(
                        card_dict['name'], card['limit_break'], card['lv'], card_dict['rarity']))
            except KeyError:
                raise
            except TypeError:
                raise

        




    def do_quest_section(self, section, *args, **kwargs):
        self.logger.info("Do quest section: {0}".format(section))
        quest_info = dict()
        quest_info['qtype'] = self.config.get(section, 'QuestId').split(',')[0]
        quest_info['qid'] = self.config.get(section, 'QuestId').split(',')[1]
        quest_info['raid'] = self.config.getint(section, 'AutoRaid')
        quest_info['fid'] = 1965350
        quest_info['retry_interval'] = self.config.getint(section, 'RetryDuration')
        quest_info['max_event_point'] = self.config.getint(section, 'MaxEventPoint')
        quest_info['auto_sell'] = self.config.getint(section, 'AutoSell')
        try:
            quest_info['get_present'] = self.config.getint(section, 'GetPresent')
        except:
            quest_info['get_present'] = 0
        if quest_info['max_event_point'] == -1:
            quest_info['max_event_point'] = sys.maxint
        count = self.config.getint(section, 'Count')
        b_infinite = True if count == -1 else False

        current = 0
        while True:
            current += 1
            if current > count and b_infinite is False:
                break
            self.logger.debug(u"#{0} 開始關卡: [{1}]".format(current, quest_info['qid']))
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
                # self.logger.debug(u"    -> 關卡完成".format(current))
                # 踏破
                try:
                    result = self.__is_meet_event_point(result, quest_info['max_event_point'])
                    if result is True:
                        break
                except Exception:
                    # not event time
                    pass
                # sell treasure
                if quest_info['auto_sell'] == 1:
                    try:
                        for earn in result['body'][1]['data']:
                            # id = earn['id']
                            idx = earn['idx']
                            # self.logger.debug(idx)
                            r = self.do_sell_item(idx)
                            if r['res'] == 0:
                                self.logger.debug(u"\t-> 賣出卡片 {0}, result = {1}".format(idx, r['res']))
                            else:
                                self.logger.error(u"\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
                                sys.exit(0)
                    except Exception:
                        self.logger.warning(u"無可販賣卡片")

                # Get presents
                self.do_present_process(quest_info['get_present'], False)
            elif result['res'] == 1:
                self.logger.warning(u"#{0} - 戰鬥失敗，已被登出".format(current))
                sleep_sec = 60 * quest_info['retry_interval']
                self.logger.info(u"等待{0}分鐘後再試...".format(quest_info['retry_interval']))
                time.sleep(sleep_sec)
                self.do_login()
            else:
                self.logger.error(u"    -> 關卡失敗".format(current))
                self.logger.debug(result)
                return
            time.sleep(0.5)
            # 魔神戰
            if quest_info['raid'] == 1:
                self.do_raid_quest()

    def do_raid_quest(self):
        r = raid_client.get_raid_boss_id(self.account_info['sid'])
        try:
            boss_id = r['boss_id']
            boss_lv = r['boss_param']['lv']
        except:
            # 非魔神戰期間
            return
        if boss_id:
            parameter = dict()
            parameter['boss_id'] = boss_id
            self.logger.debug(u"魔神來襲！魔神等級: [{0}]".format(boss_lv))
            r = raid_client.start_raid_quest(parameter, self.account_info['sid'])
            if r['res'] == 0:
                raid_client.finish_raid_quest(parameter, self.account_info['sid'])
                raid_client.get_raid_bonus(parameter, self.account_info['sid'])
            elif r['res'] == 104:
                self.logger.debug(u"魔神戰體力不足")
            elif r['res'] == 603:
                self.logger.debug(u"發現的魔神已結束")
                raid_client.finish_raid_quest(parameter, self.account_info['sid'])
                raid_client.get_raid_bonus(parameter, self.account_info['sid'])
            elif r['res'] == 608:
                self.logger.error(u"魔神戰逾時")
                raid_client.finish_raid_quest(parameter, self.account_info['sid'])
                raid_client.get_raid_bonus(parameter, self.account_info['sid'])
            else:
                self.logger.error("Unknown Error: {0}".format(r['res']))

        else:
            pass

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

    def do_totalwar_section(self, section, *args, **kwargs):
        parameter = dict()
        parameter['tid'] = 11
        count = self.config.getint(section, 'Count')
        ring = self.config.getint(section, 'Ring')
        auto_sell = self.config.getint(section, 'AutoSell')

        for i in xrange(0, count):
            self.logger.debug(u"{0}/{1} 來自公會的委托".format(i+1, count))
            ret = totalwar_client.accept_totalwar(ring, self.account_info['sid'])
            if ret['res'] == 0:
                self.logger.debug(u"Start TotalWar")
                ret = totalwar_client.start_totalwar(parameter, self.account_info['sid'])
                self.logger.debug(u"Finish TotalWar")
                ret = totalwar_client.finish_totalwar(parameter, self.account_info['sid'])
                if auto_sell == 1:
                    try:
                        for earn in ret['body'][1]['data']:
                            # id = earn['id']
                            idx = earn['idx']
                            # self.logger.debug(idx)
                            r = self.do_sell_item(idx)
                            if r['res'] == 0:
                                self.logger.debug(u"\t-> 賣出卡片 {0}, result = {1}".format(idx, r['res']))
                            else:
                                self.logger.error(u"\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
                                sys.exit(0)
                    except Exception as e:
                        self.logger.warning(u"無可販賣卡片")
            else:
                self.logger.debug(u"無法接受公會委拖")
                return

    def do_explorer_section(self, section, *args, **kwargs):
        # Hard code cid to exclude them to explorer
        except_card_idx = [7017, 7024, 7015, 51]
        r = explorer_client.get_explorer_information(self.account_info['sid'])
        if r['res'] != 0:
            self.logger.error(u"無法取得探索資訊")
            sys.exit(0)
        else:
            pickup_list = r['pickup']
        # self.logger.debug(pickup_list)

        explorer_area = self.config.getlist(section, 'area')

        for i in range(0, 3):
            # get result
            while True:
                r = explorer_client.get_explorer_result(i + 1, self.account_info['sid'])
                # No explorer data or get result success
                if r['res'] == 2308 or r['res'] == 0:
                    break
                elif r['res'] == 2302:
                    self.logger.warning(u"探索尚未結束..稍後重試")
                    time.sleep(60)
                else:
                    self.logger.warning(u"未知的探索結果")
                    self.logger.warning(r)
                    break

            area = int(explorer_area[i])
            card_idx = self.find_best_idx_to_explorer(pickup_list[area], except_card_idx)

            # go to explorer
            parameter = dict()
            parameter['explorer_idx'] = i+1
            parameter['location_id'] = area
            parameter['card_idx'] = card_idx
            parameter['pick_up'] = 1
            r = explorer_client.start_explorer(parameter, self.account_info['sid'])

    def do_buy_item_section(self, section, *args, **kwargs):
        item_type = self.config.get(section, 'Type')
        count = self.config.getint(section, 'Count')

        for i in range(0, count):
            self.logger.debug(u"#{0} 購買道具".format(i + 1))
            ret = item_client.buy_item_with_type(item_type, self.account_info['sid'])
            if ret['res'] == 0:
                self.logger.debug(u'    ->完成')
            else:
                self.logger.debug(u'    ->失敗')
                self.logger.debug(ret)

    def buy_ap_fruit(self):
        ret = item_client.buy_ap_fruit(self.account_info['sid'])
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
            # ret['res'] = 1 # mock
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
                # self.logger.error(u"Key Error:{0}, 找不到卡片idx, 可能是包包已滿，或是卡片是新的".format(e))
                # print simplejson.dumps(r, indent=4, sort_keys=True)
                # error handling for 新卡片
                for record in r['body'][3]['data']:
                    tmp = dict()
                    idx = record['idx']
                    cid = record['id']
                    tmp[idx] = cid
                    gacha_result[idx] = cid
            except Exception as e:
                self.logger.error(u"轉蛋完成，但有未知的錯誤，可能是包包滿了，無法賣出: {0}".format(r['res']))
                self.logger.debug(simplejson.dumps(r))
                raise
                return gacha_result

        elif r['res'] == 703:
            self.logger.error(u"轉蛋失敗，聖靈幣不足")
            return gacha_result
        else:
            self.logger.error(u"轉蛋失敗，未知的錯誤，無法繼續轉蛋:{0}, {1}".format(r['res'], r))
            return gacha_result
        return gacha_result

    def do_present_process(self, i_flag, b_sell):
        if i_flag == 0:
            return
        sid = self.account_info['sid']
        present_ids = present_client.get_present_list(sid)
        # self.logger.debug('禮物清單: {0}'.format(present_ids))
        while len(present_ids) > 0:
            pid = present_ids.pop(0)
            self.logger.debug("接收禮物 {0}".format(pid))
            ret = present_client.receieve_present(pid, sid)
            if ret['res'] == 0:
                # self.logger.debug(u"    -> 接收成功")
                pass
            else:
                self.logger.debug(u"    -> 接收失敗: {0}".format(ret))
            if b_sell is True:
                ret = self.do_sell_item(pid)
                self.logger.debug("sell present result: {0}".format(ret['res']))

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

    def find_best_idx_to_explorer(self, area_pickup_list, except_card_idx=[]):
        # for pickup in pickup_list:
        # self.logger.debug(pickup)
        # card_list = self.CC_GetAllData()['body'][6]['data']
        card_list = alldata_client.get_alldata(self.account_info['sid'])['body'][6]['data']

        self.logger.debug("Pickup attribute home: {0}".format(area_pickup_list['home']))
        self.logger.debug("Pickup attribute job type: {0}".format(area_pickup_list['jobtype']))
        self.logger.debug("Pickup attribute weapontype: {0}".format(area_pickup_list['weapontype']))
        temp_idx = None
        for card in card_list:
            if card['type'] == 0:
                temp_idx = card['idx']
                temp_id = card['id']
                card_doc = self.db.charainfo.find_one({"cid": card['id']})
                if card_doc:
                    # self.logger.debug("home:{0}, {1}".format(card_doc['home'], type(card_doc['home'])))
                    # self.logger.debug("jobtype:{0}".format(card_doc['jobtype']))
                    # TODO: bug here, weapon type is not equal to battletype
                    # how to solve it due to mongodb has no weapon type record
                    # self.logger.debug("weapontype:{0}".format(card_doc['battletype']))
                    if (int(area_pickup_list['home']) == card_doc['home']) or (
                            int(area_pickup_list['jobtype']) == card_doc['jobtype']) or (
                            int(area_pickup_list['weapontype']) == card_doc['battletype']):

                        temp_idx = card['idx']
                        if temp_id in except_card_idx:
                            continue
                        if card_doc['rarity'] == 5:
                            continue
                        self.logger.debug(u"Found pickup card! {0}".format(card_doc['name']))
                        self.logger.debug(u"{0} is picked to eplorer".format(temp_idx))
                        return temp_idx
                    else:
                        # this card does not fit pick up criteria
                        continue
                else:
                    # DB has no record to do matching
                    continue
                # self.logger.error("Cannot find card id {0} in database, please update DB".format(card['id']))
                # self.logger.debug("{0} is picked to eplorer".format(temp_idx))
            else:
                # card is not character
                continue
        return temp_idx

    def __is_meet_event_point(self, result, max_event_point):
        # 踏破活動
        event_point = result['body'][2]['data']['point']
        fever_rate = 1.0
        self.logger.info("目前戰功： {0}".format(event_point))
        try:
            fever_rate = result['earns']['treasure'][0]['fever']
        except Exception as e:
            pass
        self.logger.debug("目前戰功倍率：%s" % fever_rate)

        if max_event_point and event_point >= max_event_point:
            self.logger.warning("超過最大戰功設定上限")
            return True
        else:
            return False


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle automation tool")
    parser.add_argument('-c', '--config', help='Config file path', required=True)
    parser.add_argument('-a', '--action', help='Execute specific section of config file', required=False)
    args = parser.parse_args()
    config_file = args.config
    cc = ChainChronicle(config_file)
    cc.load_config()
    if args.action is not None:
        # force overwrite config flow and just do the action from args
        cc.action_list = [args.action]
    cc.start()

if __name__ == '__main__':
    main()


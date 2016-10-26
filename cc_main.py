# -*- coding: utf-8 -*
import argparse
import logging
import os
import sys
import time
import urllib
from random import randint

import simplejson

import utils.cc_logger
import utils.db_operator
import utils.enhanced_config_parser
import utils.poster
from lib import alldata_client
from lib import explorer_client
from lib import gacha_client
from lib import item_client
from lib import present_client
from lib import quest_client
from lib import raid_client
from lib import recovery_client
from lib import subjugation_client
from lib import totalwar_client
from lib import user_client
from lib import friend_client


class ChainChronicle(object):

    def __init__(self, c, console_log_level=logging.DEBUG):
        if os.path.isfile(c):
            self.config_file = c
        else:
            raise IOError("{0} is not exist".format(c))

        self.poster = utils.poster.Poster

        self.action_list = list()
        self.account_info = dict()
        log_id = os.path.basename(os.path.splitext(self.config_file)[0])
        self.__init_logger(log_id, console_log_level)
        self.config = utils.enhanced_config_parser.EnhancedConfigParser()
        self.action_mapping = {
            'QUEST': self.do_quest_section,
            'GACHA': self.do_gacha_section,
            'BUY': self.do_buy_item_section,
            'EXPLORER': self.do_explorer_section,
            'WASTE_MONEY': self.do_waste_money,
            'TOTALWAR': self.do_totalwar_section,
            'SUBJUGATION': self.do_subjugation_section,
            'STATUS':  self.do_show_status,  # no need section in config
            'LIST_CARDS':  self.do_show_all_cards,  # no need section in config
            'DAILY_TICKET': self.do_daily_gacha_ticket,  # no need section in config
            'LIST_ALLDATA': self.do_show_all_data,  # no need section in config
            'PASSWORD': self.do_set_password,  # no need section in config
            'PRESENT': self.do_get_present, # no need section in config, get non-cards presents
            'QUERY_FID': self.do_query_fid # no need section in config, get non-cards presents

        }


    def __init_logger(self, log_id, level):
        self.logger = utils.cc_logger.CCLogger.get_logger(log_id, level)

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
        #url = 'http://v267b.cc.mobimon.com.tw/session/login'
        url = 'http://v267b.cc.mobimon.com.tw/session/login'
        headers = {'Cookie': 'sid=INVALID'}
        data = {
            'UserUniqueID': self.account_info['uid'],
            'Token': self.account_info['token'],
            'OS':1
        }
        payload_dict = {
          "APP": {
            "Version": "2.67",
            "Revision": "2014",
            "time": time.time(),
            "Lang": "Chinese"
        },
            "DEV": data
        }
        payload = 'param=' + urllib.quote_plus(simplejson.dumps(payload_dict))
        ret = self.poster.post_data(url, headers, None, payload, **data)
        # self.logger.debug(ret['login']['sid'])
        try:
            self.account_info['sid'] = ret['login']['sid']
        except KeyError:
            msg = u"無法登入, Message = {0}".format(ret['msg'])
            self.logger.error(msg)
            raise KeyError(msg)

    def do_daily_gacha_ticket(self, section, *args, **kwargs):
        r = item_client.get_daily_gacha_ticket(self.account_info['sid'])
        self.logger.debug(r)

    def do_set_password(self, section, *args, **kwargs):
        r = user_client.get_account(self.account_info['sid'])
        print(simplejson.dumps(r, sort_keys=True, indent=2))

        r = user_client.set_password('aaa123', self.account_info['sid'])
        print(simplejson.dumps(r, sort_keys=True, indent=2))

    def do_show_all_data(self, section, *args, **kwargs):
        r = alldata_client.get_alldata(self.account_info['sid'])
        print(simplejson.dumps(r, sort_keys=True, indent=2))

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

        user_info = r['body'][4]['data']
        for key, data in user_info.iteritems():
            self.logger.debug(u"{0} = {1}".format(key, data))

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
                card_dict = utils.db_operator.DBOperator.get_cards('cid', cid)[0]
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
        quest_info['fid'] = self.config.getint(section, 'Fid')
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
            # self.logger.debug("Quest finish result = {0}".format(result))
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
                            self.logger.debug(earn)
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
                # if 'recovery_val' in result.keys():
                try:
                    self.logger.debug(u'回復AP {0}'.format(result['recovery_val']))
                except:
                    pass
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
                self.do_raid_quest(fid=quest_info['fid'])

    def do_raid_quest(self, **kwargs):
        # r = raid_client.get_raid_boss_id(self.account_info['sid'])
        # self.logger.debug(r)
        # self.logger.debug(type(r))
        # try:
        #    boss_id = r['boss_id']
        #    boss_lv = r['boss_param']['lv']
        #except:
        #    raise
            # 非魔神戰期間
        #    return
        boss_id = raid_client.get_raid_info(self.account_info['sid'], 'id')
        boss_lv = raid_client.get_raid_info(self.account_info['sid'], 'lv')
        if boss_id:
            parameter = dict()
            parameter['boss_id'] = boss_id
            # parameter['fid'] = '1965350'
            parameter['fid'] = kwargs['fid']
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

    def do_subjugation_section(self, section, *args, **kwargs):
        try:
            count = self.config.getint(section, 'Count')
        except:
            count = 1
        if count == -1:
            count = sys.maxint
        for i in range(0, count):
            self.do_subjugation(section, *args, **kwargs)

    def do_subjugation(self, section, *args, **kwargs):
        parameter = dict()
        parameter['jid'] = self.config.getint(section, 'Jid')
        parameter['fid'] = self.config.getint(section, 'Fid')
        parties = self.config.options_with_prefix(section, 'pt_')
        parameter['pt_cids'] = list()
        for party in parties:
            parameter['pt_cids'].append(self.config.getlist(section, party))

        # self.logger.debug(u"取得討伐戰資料")
        # r = subjugation_client.check_participant(parameter, self.account_info['sid'])
        # if != 0:
            # self.logger.debug(r)
            # return

        # get ecnt
        r = alldata_client.get_alldata(self.account_info['sid'])
        # r_json = simplejson.dumps(r, indent=2)
        # print r_json
        try:
            ecnt = r['body'][18]['data']['reached_expedition_cnt'] + 1
            parameter['ecnt'] = ecnt
        except KeyError:
            self.logger.debug("Cant get ecnt data")
            parameter['ecnt'] = 1

        try:
            rare_expedition_cnt = r['body'][18]['data']['rare_expedition']['expedition_cnt']
        except:
            pass


        try:
            trying = r['body'][18]['data']['trying']
        except:
            trying = False

        if parameter['ecnt'] > 40:
            parameter['ecnt'] = 40
        # parameter['ecnt'] = 40
        self.logger.info(u"第{0}次討伐".format(parameter['ecnt']))
        self.logger.debug(u"取得討伐戰資料")
        if trying is False:
            r = subjugation_client.try_subjugation(parameter, self.account_info['sid'])
            if r['res'] == 0:
                self.logger.debug(u"進入討伐戰")
                data_idx = 1
            else:
                self.logger.error(r['msg'])
                return
        else:
            self.logger.warning(u"已經在討伐中")
            data_idx = 19

        self.logger.debug(u"取得關卡id")
        base_id_list = list()
        wave_list = list()
        rare_base_id = None
        rare_max_wave = None
        # print simplejson.dumps(r['body'][data_idx]['data'])
        for data in r['body'][data_idx]['data']:
            try:
                is_rare = data['rare']
            except:
                is_rare = False

            if is_rare:
                # rare base id should be played in the end
                rare_base_id = data['base_id']
                rare_max_wave = data['max_wave']
            else:
                base_id_list.append(data['base_id'])
                wave_list.append(data['max_wave'])

        # append rare id in the end
        if rare_base_id is not None:
            base_id_list.append(rare_base_id)
            wave_list.append(rare_max_wave)

        parameter['wave_list'] = wave_list

        self.logger.debug(u"關卡id = {0}".format(base_id_list))
        self.logger.debug(u"wave_list = {0}".format(wave_list))
        # sys.exit(0)

        # Start
        # base_id_list = [6]
        # wave_list = [3]
        for idx, bid in enumerate(base_id_list):
            # self.logger.debug(u"Using Party {0}".format(idx))
            self.logger.debug(u'討伐關卡: {0}'.format(bid))
            parameter['bid'] = bid
            parameter['pt'] = idx
            parameter['wave'] = wave_list[idx]
            parameter['pt_cid'] = parameter['pt_cids'][idx]

            # Start entry
            # print parameter
            r = subjugation_client.start_subjugation(parameter, self.account_info['sid'])
            if r['res'] == 0:
                pass
            elif r['res'] == 1919:
                self.logger.debug(u"already finished")
                continue
            elif r['res'] == 1905:
                self.logger.debug(r)
                continue
            else:
                self.logger.debug(r)
                return
            # result = simplejson.dumps(r, indent=2)
            # print result
            # self.logger.debug("Start entry = {0}".format(r))

            # Get Result
            r = subjugation_client.finish_subjugation(parameter, self.account_info['sid'])
            if r['res'] == 0:
                self.logger.debug(u'討伐關卡: {0} 完成'.format(bid))
            else:
                self.logger.debug(r)
                return

            # result = simplejson.dumps(r, indent=2)
            # print result
            # self.logger.debug("End entry = {0}".format(r))

    def do_gacha_section(self, section, *args, **kwargs):
        gacha_info = dict()

        gacha_info['count'] = self.config.getint(section, 'Count')
        gacha_info['gacha_type'] = self.config.getint(section, 'Type')

        try:
            gacha_info['auto_sell'] = self.config.getint(section, 'AutoSell')
        except :
            gacha_info['auto_sell'] = 0

        try:
            gacha_info['verbose'] = self.config.get('Verbose')
        except:
            gacha_info['verbose'] = 0

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


    def do_waste_money(self, section, *args, **kwargs):
        parameter = dict()
        card_idx = [358771956]
        waste_money_round = 211949980 / 1000
        remaining = waste_money_round

        for i in range(0, waste_money_round):
            parameter['explorer_idx'] = 1
            r = explorer_client.cancel_explorer(parameter, self.account_info['sid'])
            parameter['location_id'] = 0
            parameter['card_idx'] = 358771956
            parameter['pickup'] = 0
            r = explorer_client.start_explorer(parameter, self.account_info['sid'])
            if r['res'] == 2311:
                parameter['pickup'] = 1
                explorer_client.start_explorer(parameter, self.account_info['sid'])
            elif r['res'] == 0:
                pass
            else:
               break
            remaining -= 1
            # sys.exit(0)
            print 'remaining = {0} rounds'.format(remaining)





    def do_explorer_section(self, section, *args, **kwargs):
        # Hard code cid to exclude them to explorer
        except_card_id = [7017, 7024, 7015, 51]
        r = explorer_client.get_explorer_information(self.account_info['sid'])
        if r['res'] != 0:
            self.logger.error(u"無法取得探索資訊")
            sys.exit(0)
        else:
            pickup_list = r['pickup']
        # self.logger.debug(pickup_list)

        explorer_area = self.config.getlist(section, 'area')

        # debug section
        # card_idx = self.find_best_idx_to_explorer(pickup_list[3], except_card_id)
        # print card_idx
        #sys.exit(0)

        # Get non-cards presents
        self.do_present_process(1, 0, 'item')

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
                elif r['res'] == 1:
                    self.logging.warning(u'已被登出, 稍後重試')
                    time.sleep(60*5)
                    self.do_login()
                else:
                    self.logger.warning(u"未知的探索結果")
                    self.logger.warning(r)
                    break

            area = int(explorer_area[i])
            print pickup_list[area], except_card_id
            card_idx, card_id = self.find_best_idx_to_explorer(pickup_list[area], except_card_id)
            except_card_id.append(card_id)

            # go to explorer
            parameter = dict()
            parameter['explorer_idx'] = i+1
            parameter['location_id'] = area
            parameter['card_idx'] = card_idx
            parameter['pickup'] = 1
            r = explorer_client.start_explorer(parameter, self.account_info['sid'])
            if r['res'] == 2311:
                # self.logger.debug(u"pickup value error, retry")
                parameter['pickup'] = 0
                explorer_client.start_explorer(parameter, self.account_info['sid'])


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
            if gacha_info['gacha_type'] in [3, 8]:
                time.sleep(3)
            self.logger.info(u"#{0}: 轉蛋開始！".format(i + 1))
            gacha_result = self.do_gacha(gacha_info['gacha_type'])
            #self.logger.debug(u"得到卡片: {0}".format(gacha_result.values()))
            self.logger.debug(u"得到卡片: {0}".format(gacha_result.values()))
            if gacha_info['verbose']:
                cids = gacha_result.values()
                for cid in cids:
                    cards = utils.db_operator.DBOperator.get_cards('cid', cid)
                    # if not cards or 'name' not in cards[0] or 'rarity' not in cards[0]:
                    # use BIF all() to check if the dict has key 'name' AND 'rarity'
                    if not cards or not all([i in cards[0].keys() for i in ['name', 'rarity']]):
                        self.logger.debug(cid)
                    else:
                        card = cards[0]  # cid is key index
                        msg = 'Name={0}, Rarity={1}'.format(card['name'].encode('utf-8'), card['rarity'])
                        self.logger.debug(msg)
            #if gacha_result is None or len(gacha_result) == 0:
            if not gacha_result:
                self.logger.debug("Gacha Error")
                break

            # Auto sell cards and keep some cards
            if gacha_info['auto_sell'] == 1:
                for cidx, cid in gacha_result.iteritems():
                    if str(cid) in gacha_info['keep_cards']:
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
        """recovery stamina by using AP fruit slice first, if failed, then try fruit"""
        parameter = dict()
        parameter['type'] = 1
        parameter['item_id'] = 16
        parameter['use_cnt'] = 10
        ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
        if ret['res'] != 0:
            parameter['item_id'] = 1
            ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
        return ret

    def do_gacha(self, g_type):
        gacha_result = dict()
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
            except KeyError:
                # self.logger.error(u"Key Error:{0}, 找不到卡片idx, 可能是包包已滿，或是卡片是新的".format(e))
                # print simplejson.dumps(r, indent=4, sort_keys=True)
                # error handling for 新卡片
                for record in r['body'][3]['data']:
                    tmp = dict()
                    idx = record['idx']
                    cid = record['id']
                    tmp[idx] = cid
                    gacha_result[idx] = cid
            except Exception:
                self.logger.error(u"轉蛋完成，但有未知的錯誤，可能是包包滿了，無法賣出: {0}".format(r['res']))
                self.logger.debug(simplejson.dumps(r))
                # raise
                return gacha_result

        elif r['res'] == 703:
            self.logger.error(u"轉蛋失敗，聖靈幣不足")
            return gacha_result
        elif r['res'] == 207:
            time.sleep(3)
            self.logger.debug('retry')
            return self.do_gacha(parameter['type'])
        else:
            self.logger.error(u"轉蛋失敗，未知的錯誤，無法繼續轉蛋:{0}, {1}".format(r['res'], r))
            raise Exception('Unable to gacha')
            # return gacha_result
        return gacha_result

    def do_query_fid(self, section, *args, **kwargs):
        oid = 114386130
        result = friend_client.query_fid(self.account_info['sid'], oid)
        for key, data in result['friend'].iteritems():
            self.logger.debug(u"{0} = {1}".format(key, data))

    def do_get_present(self, section, *args, **kwargs):
        self.do_present_process(1, 0, 'item')

    def do_present_process(self, i_flag, b_sell, item_type=None):
        if i_flag == 0:
            return
        sid = self.account_info['sid']
        present_ids = present_client.get_present_list(sid, item_type)
        self.logger.debug('禮物清單: {0}'.format(present_ids))
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
        url = 'http://v267b.cc.mobimon.com.tw/card/sell'
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

    def find_best_idx_to_explorer(self, area_pickup_list, except_card_id=[]):
        # for pickup in pickup_list:
        # self.logger.debug(pickup)
        # card_list = self.CC_GetAllData()['body'][6]['data']
        card_list = alldata_client.get_alldata(self.account_info['sid'])['body'][6]['data']

        self.logger.debug("Pickup attribute home: {0}".format(area_pickup_list['home']))
        self.logger.debug("Pickup attribute job type: {0}".format(area_pickup_list['jobtype']))
        self.logger.debug("Pickup attribute weapontype: {0}".format(area_pickup_list['weapontype']))
        temp_idx = None
        for card in card_list:
            if card['id'] in except_card_id:
                self.logger.debug(u"跳過保留不去探索的卡片: {0}".format(card['id']))
                continue
            if card['type'] == 0:
                temp_idx = card['idx']
                card_doc = None
                card_doc_list = utils.db_operator.DBOperator.get_cards('cid', card['id'])
                if len(card_doc_list) > 0:
                    card_doc = card_doc_list[0]
                if card_doc:
                    if 'rarity' in card_doc and card_doc['rarity'] >= 5:
                        continue
                    # self.logger.debug("home:{0}, {1}".format(card_doc['home'], type(card_doc['home'])))
                    # self.logger.debug("jobtype:{0}".format(card_doc['jobtype']))
                    # TODO: bug here, weapon type is not equal to battletype
                    # how to solve it due to mongodb has no weapon type record
                    # self.logger.debug("weapontype:{0}".format(card_doc['battletype']))
                    if (int(area_pickup_list['home']) == card_doc['home']) or (
                            int(area_pickup_list['jobtype']) == card_doc['jobtype']) or (
                            int(area_pickup_list['weapontype']) == card_doc['battletype']):

                        temp_idx = card['idx']
                        self.logger.debug(u"Found pickup card! {0}".format(card_doc['name']))
                        self.logger.debug(u"{0} is picked to eplorer".format(temp_idx))
                        # print card
                        return temp_idx, card['id']
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
        self.logger.warning(u"找不到適合的探索角色，使用[{0}]".format(card_doc['name']))
        return temp_idx, card['id']

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
    parser.add_argument('-l', '--list_command', help='List commands', required=False, action='store_true')

    args = parser.parse_args()
    config_file = args.config
    cc = ChainChronicle(config_file)
    cc.load_config()
    if args.list_command:
        print "Valid actions:"
        print cc.action_mapping.keys()
        sys.exit(0)

    if args.action is not None:
        # force overwrite config flow and just do the action from args
        cc.action_list = [args.action]
    cc.start()

if __name__ == '__main__':
    main()


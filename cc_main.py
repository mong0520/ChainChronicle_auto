#-*- coding: utf-8 -*-
#!/usr/bin/python
import argparse
import logging
import os
import sys
import time
import urllib
from random import randint
try:
    import socket
    import socks
except:
    pass

import simplejson

import utils.cc_logger
import utils.db_operator
import utils.enhanced_config_parser
import utils.poster
import requests
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
from lib import weapon_client
from lib import tutorial_client
from lib import debug_client
from lib import teacher_disciple_client

'''
在Assembly-CSharp.dll中找'StartCoroutine'可以看到所有api call
'''

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
            'QUERY_FID': self.do_query_fid, # no need section in config, get non-cards presents
            'COMPOSE': self.do_compose,
            'TUTORIAL': self.do_pass_tutorial,
            'DRAMA': self.do_play_drama_auto,
            'POC': self.do_poc,
            'TEACHER': self.do_teacher_section,
            'DISCIPLE': self.do_disciple_section
            #'SECTION_NAME': sefl.function_name
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
                    try:
                        self.account_info['reuse_sid'] = self.config.getint(section, 'ReuseSid')
                    except:
                        self.account_info['reuse_sid'] = 0

    def set_proxy(self):
        try:
            self.logger.debug('Use socks5 proxy')
            socks_info = self.config.get('GLOBAL', 'Socks5')
            # print socks_info.split(':')
            [socks5_addr, socks5_port] = socks_info.split(':')
            socks.set_default_proxy(socks.SOCKS5, socks5_addr, int(socks5_port))
            socket.socket = socks.socksocket
        except Exception as e:
            self.logger.warning(e)
            self.logger.debug('Not use socks5 proxy')

    def start(self):
        if self.account_info['reuse_sid']:
            reuse_sid = self.get_local_sid()
            self.account_info['sid'] = reuse_sid
            try:
                self.do_show_status(None)
                self.logger.debug('Reuse sid {0}'.format(reuse_sid))
            except Exception as e:
                self.logger.warning('SID is invalid, re-login: {0}'.format(e))
                self.do_login()
        else:
            self.do_login()

        # for action in self.action_list:
        action_idx = 0
        while True:
            if action_idx >= len(self.action_list):
                break
            try:
                self.do_action(self.action_list[action_idx])
                action_idx += 1
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(e)
                time.sleep(3)
                self.logger.debug('Retry section {0}'.format(self.action_list[action_idx]))
                continue


    def get_local_sid(self):
        sid_file = '.' + os.path.basename(os.path.splitext(self.config_file)[0])
        try:
            with open(sid_file, 'r') as f:
                sid = f.read().strip()
            self.logger.debug(u'Found sid {0}, try to reuse it'.format(sid))
            return sid
        except Exception as e:
            self.logger.warning(e)
            return None


    def do_action(self, action_name):
        for action, action_function in self.action_mapping.iteritems():
            # if action == action_name:
            if action_name.startswith(action):
                self.logger.info("### Current Flow = {0} ###".format(action_name))
                action_function(action_name)

    def do_login(self):
        url = 'http://v272.cc.mobimon.com.tw/session/login'
        headers = {
            'Cookie': 'sid=INVALID'
        }
        data = {
            'UserUniqueID': self.account_info['uid'],
            'Token': self.account_info['token'],
            'OS': 2
        }
        payload_dict = {
          "APP": {
            "Version": "2.72",
            "Revision": "2014",
            "time": time.time(),
            "Lang": "Chinese"
        },
            "DEV": data
        }
        payload = 'param=' + urllib.quote_plus(simplejson.dumps(payload_dict))
        # print url
        # print payload
        ret = self.poster.post_data(url, headers, None, payload, **data)
        # self.logger.debug(ret)
        # sys.exit(0)
        try:
            self.account_info['sid'] = ret['login']['sid']
            self.logger.debug('sid = {0}'.format(ret['login']['sid']))
            sid_file = '.' + os.path.basename(os.path.splitext(self.config_file)[0])
            with open(sid_file, 'w') as f:
                f.write(self.account_info['sid'])

        except KeyError:
            msg = u"無法登入, Message = {0}".format(ret['msg'])
            self.logger.error(msg)
            raise KeyError(msg)


    def do_teacher_section(self, section, *args, **kwargs):
        accept = self.config.get(section, 'Accept')
        r = teacher_disciple_client.toggle_acceptance(self.account_info['sid'], accept=accept)
        self.logger.debug(r['body'][0]['data'])



    def do_disciple_section(self, section, *args, **kwargs):
        tid = self.config.get(section, 'Teacher_Id')
        # teacher_disciple_client.IS_DISCIPLE_GRADUATED = 1
        if teacher_disciple_client.IS_DISCIPLE_GRADUATED:
            for i in [5,10,15,20,25,30,35,40,45]:
                r = teacher_disciple_client.thanks_achievement(self.account_info['sid'], lv=i)
                self.logger.debug('UID {0} sends gift for LV {1}, res= {2}'.format(self.account_info['uid'], i, r['res']))
                if r['res'] != 0:
                    self.logger.warning('UID {0} is failed to send gift teacher {1}, msg = {2}'.format(self.account_info['uid'], tid, r))
                    

            #r = teacher_disciple_client.reset_from_disciple(self.account_info['sid'])
            #self.logger.debug('UID {0} reset from disciple {1}'.format(self.account_info['uid'], r['res']))


            r = teacher_disciple_client.thanks_thanks_graduate(self.account_info['sid'])
            self.logger.debug('UID {0} is graduated!, res = {1}'.format(self.account_info['uid'], r['res']))
            if r['res'] != 0:
                self.logger.warning('UID {0} is failed to graduate, msg = {1}'.format(self.account_info['uid'], r))
        else:
            # 徒：申請師父
            r = teacher_disciple_client.apply_teacher(self.account_info['sid'], tid=tid)
            self.logger.debug('UID {0} applies teacher {1}, res = {2}'.format(self.account_info['uid'], tid, r['res']))
            if r['res'] != 0:
                self.logger.warning('Apply teacher failed: {0}'.format(r))
                raise Exception('Applay teacher failed!')


    def do_poc(self, section, *args, **kwargs):
        import json
        # r = debug_client.debug_poc(self.account_info['sid'],
            # path='/friend/list')
        # 師：開放徒弟
        # r = debug_client.debug_poc(self.account_info['sid'],
        #     path='/teacher/toggle_acceptance', accept=1, only_friend=0)

        # 師：送禮物
        # r = debug_client.debug_poc(self.account_info['sid'],
            # path='/teacher/rewards_daily_achievement', present='f')

        r = debug_client.debug_poc(self.account_info['sid'],
            path='/friend/list')
        print json.dumps(r, encoding="UTF-8", ensure_ascii=False)

        # 19073918, 19609396, 19609399

        # r = debug_client.debug_poc(self.account_info['sid'],
        #     path='/teacher/reset_from_disciple')

        # 徒：申請師父
        # r = debug_client.debug_poc(self.account_info['sid'],
            # path='/teacher/apply', tid=1965350)

        # 徒：等級到了，回禮
        # r = debug_client.debug_poc(self.account_info['sid'],
            # path='/teacher/thanks_achievement', lv=15)

        # 徒：一般回禮
        # r = debug_client.debug_poc(self.account_info['sid'],
        #     path='/teacher/cheer_by_disciple')

        # 查看開放師父清單
        # r = debug_client.debug_poc(self.account_info['sid'],
            # path='/teacher/candidate_list', limit=0)


        # 徒：畢業了，感謝師父
        # r = debug_client.debug_poc(self.account_info['sid'],
             # path='/teacher/thanks_graduate', firend=1)
        '''
        import pprint
        class MyPrettyPrinter(pprint.PrettyPrinter):
            def format(self, object, context, maxlevels, level):
                if isinstance(object, unicode):
                    return (object.encode('utf8'), True, False)
                return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

        MyPrettyPrinter().pprint(r)
        '''
        # print simplejson.dumps(r, ensure_ascii=False).encode('utf-8')


    def do_play_drama_auto(self, section, *args, **kwargs):
        quest_info = dict()
        results = list()
        parameter = dict()
        parameter['type'] = 1 # 體果
        parameter['item_id'] = 1
        parameter['use_cnt'] = 1
        lv_threshold = 50
        current_lv = 1
        while True:
            qtype, qid, lv = self.__get_latest_quest()
            if lv >= lv_threshold:
                self.logger.debug('Lv exceeds threshold, break'.format(lv_threshold))
                teacher_disciple_client.IS_DISCIPLE_GRADUATED = True 
                break
            else:
                if lv != current_lv:
                    self.logger.debug('LV = {0}'.format(lv)) 
                current_lv = lv
            # self.logger.debug(u'下一個關卡為: {0},{1}'.format(qtype, qid))
            results[:] = []
            quest_info['qtype'] = qtype
            quest_info['qid'] = qid
            quest_info['fid'] = 1965350

            # workaround, 從response中無法判斷qtype為5的quest是寶物或是戰鬥，只好都試試看
            result = quest_client.get_treasure(quest_info, self.account_info['sid'])
            results.append(int(result['res']))
            # self.logger.debug(result)

            result = quest_client.start_quest(quest_info, self.account_info['sid'])
            results.append(int(result['res']))
            # self.logger.debug(result)

            result = quest_client.finish_quest(quest_info, self.account_info['sid'])
            results.append(int(result['res']))
            # self.logger.debug(result)

            # self.do_get_present('PRESENT')

            # 體力不足
            if 103 in results:
                # 體果
                ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
                if ret['res'] == 0:
                    continue
                else:
                    # 精靈石
                    parameter['type'] = 0
                    ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
                    if ret['res'] == 0:
                        continue
                    else:
                        break

            # Unknown error, force break
            if 0 not in results:
                break


    def do_pass_tutorial(self, section, *args, **kwargs):
        import uuid
        tutorial_count = self.config.getint(section, 'Count')
        tid_list = range(0, 21)
        tutorail_package = [
            {'tid': 0, 'qid': None},
            {'tid': 1, 'qid': None},
            {'tid': 2, 'qid': None},
            {'tid': 3, 'qid': 210001},
            {'tid': 4, 'qid': 210001},
            {'tid': 5, 'qid': None},
            {'tid': 6, 'qid': 210002},
            {'tid': 7, 'qid': None},
            {'tid': 8, 'qid': 210101},
            {'tid': 9, 'qid': None},
            {'tid': 10, 'qid': 210101},
            {'tid': 11, 'qid': None},
            {'tid': 12, 'qid': None},
            {'tid': 13, 'qid': 210102},
            {'tid': 14, 'qid': None},
            {'tid': 15, 'qid': 210102},
            {'tid': 16, 'qid': None},
            {'tid': 17, 'qid': 215000},
            {'tid': 18, 'qid': 215000},
            {'tid': 19, 'qid': None},
            {'tid': 20, 'qid': None}
        ]
        for i in range(0, tutorial_count):
            # self.account_info['uid'] = '{0}{1}'.format('test', str(uuid.uuid4()))
            account_uuid = str(uuid.uuid4())
            self.config.set('GENERAL', 'Uid', account_uuid)
            self.account_info['uid'] = account_uuid
            self.do_login()

            self.logger.debug(u'{0}/{1} - 開始新帳號'.format(i+1, tutorial_count))
            for tutorial in tutorail_package:
                if tutorial['qid']:
                    r = tutorial_client.tutorial(self.account_info['sid'], entry=True, tid=tutorial['tid'], pt=0)
                    quest_info = dict()
                    quest_info['qid'] = tutorial['qid']
                    quest_info['fid'] = 1965350
                    r = quest_client.finish_quest(quest_info, self.account_info['sid'])
                    # print r
                else:
                    if tutorial['tid'] == 1:
                        r = tutorial_client.tutorial(self.account_info['sid'], tid=tutorial['tid'],
                            name='Allen', hero='Allen')
                        # print r
                    else:
                        r = tutorial_client.tutorial(self.account_info['sid'], tid=tutorial['tid'])
                        # print r
            self.logger.debug(u'新帳號完成新手教學，UID = {0}'.format(self.account_info['uid']))
            self.do_get_present('PRESENT')




    def do_daily_gacha_ticket(self, section, *args, **kwargs):
        r = item_client.get_daily_gacha_ticket(self.account_info['sid'])
        self.logger.slack(r)

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
                if card_dict and card_dict['rarity'] >= 5:
                    self.logger.debug(u"{0}-{1}, 界限突破：{2}, 等級: {3}, 稀有度: {4}".format(
                        card_dict['title'], card_dict['name'], card['limit_break'], card['lv'], card_dict['rarity']))
                    self.logger.debug(int(card['idx']))
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
                # print simplejson.dumps(result, ensure_ascii=True)
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
            # 魔神戰
            if quest_info['raid'] == 1:
                time.sleep(0.1)
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

    # def do_compose(self, section, *args, **kwargs):
    #     '''
    #     只合三星*5
    #     '''
    #     count = self.config.getint(section, 'Count')
    #     item_type = 'itm_weapon'
    #     for k in range(0, count):
    #         weapon_list = list()
    #         for i in range(0, 5):
    #             ret = item_client.buy_item_with_type(item_type, self.account_info['sid'])
    #             weapon_list.append(ret['body'][1]['data'][0]['idx'])
    #         ret = weapon_client.compose(self.account_info['sid'], weapon_list)
    #         print ret

    def do_compose(self, section, *args, **kwargs):
        """
        以1張5星 +  3張4星鍊金
        """
        count = self.config.getint(section, 'Count')
        item_type = 'itm_weapon_bow'
        weapon_list_rank3 = list()
        weapon_list_rank4 = list()
        # weapon_list_rank5 = list()
        weapon_base_rank5_idx = None # 基底武器

        for i in range(0, count):
            # 沒有5星武器時，先鍊出一把五星武器
            buy_count = 5
            if weapon_base_rank5_idx:
                buy_count = 4
            # 買三星武器
            for j in range(0, buy_count):
                ret = item_client.buy_item_with_type(item_type, self.account_info['sid'])
                weapon_list_rank3.append(ret['body'][1]['data'][0]['idx'])

            # 五把三星器武器，鍊成四星武器
            if len(weapon_list_rank3) == 5:
                # self.logger.info(u'開始鍊金 -  3星*5')
                # self.logger.debug(weapon_list_rank3)
                ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank3)
                weapon_list_rank3[:] = []
                # pprint.pprint(ret)
                idx = ret['body'][1]['data'][0]['idx']
                item_id = ret['body'][1]['data'][0]['id']
                # print idx, item_id
                # print item_id
                # weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
                # self.logger.info('得到武器 {0}'.format(weapon_list[0]['name'].encode('utf-8')))
                weapon_list_rank4.append(idx)

            # 有一張基底五星武器，且有四張三星武器
            if weapon_base_rank5_idx and len(weapon_list_rank3) == 4:
                # self.logger.info(u'開始鍊金 -  5星*1 + 3星*4')
                weapon_list_rank3.append(weapon_base_rank5_idx)
                ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank3)
                weapon_list_rank3[:] = []
                # pprint.pprint(ret)
                try:
                    idx = ret['body'][1]['data'][0]['idx']
                    item_id = ret['body'][1]['data'][0]['id']
                except:
                    import pprint
                    pprint.pprint(ret)
                    raise
                weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
                # print idx, item_id
                if int(item_id) in [85200, 26011, 26068, 85200]:
                    self.logger.info('{0}/{1} - 鍊金完成，得到神器!!! {2}'.format(i, count, weapon_list[0]['name'].encode('utf-8')))
                    weapon_base_rank5_idx = None
                    break
                else:
                    weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
                    self.logger.info('{0}/{1} - 鍊金完成，得到武器: {2}'.format(i, count, weapon_list[0]['name'].encode('utf-8')))
                    weapon_base_rank5_idx = idx

            # 鍊出做為基底的五星武器
            elif len(weapon_list_rank4) == 5:
                    # self.logger.info(u'開始鍊金 -  4星*5')
                    ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank4)
                    weapon_list_rank4[:] = []
                    # pprint.pprint(ret)
                    idx = ret['body'][1]['data'][0]['idx']
                    item_id = ret['body'][1]['data'][0]['id']
                    weapon_base_rank5_idx = idx

    # def do_compose(self, section, *args, **kwargs):
    #     """
    #     以1張5星 +  4張4星鍊金, 改成用bitmask會不會比較general?
    #     """
    #     count = self.config.getint(section, 'Count')
    #     item_type = 'itm_weapon'
    #     weapon_list_rank3 = list()
    #     weapon_list_rank4 = list()
    #     # weapon_list_rank5 = list()
    #     weapon_base_rank5_idx = None # 基底武器
    #     for i in range(0, count):
    #         # 50戒
    #         for i in range(0, 5):
    #             ret = item_client.buy_item_with_type(item_type, self.account_info['sid'])
    #             weapon_list_rank3.append(ret['body'][1]['data'][0]['idx'])

    #         self.logger.info(u'開始鍊金 -  3星*5')
    #         ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank3)
    #         weapon_list_rank3[:] = []
    #         # pprint.pprint(ret)
    #         idx = ret['body'][1]['data'][0]['idx']
    #         item_id = ret['body'][1]['data'][0]['id']
    #         # print idx, item_id
    #         # print item_id
    #         # weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
    #         # self.logger.info('得到武器 {0}'.format(weapon_list[0]['name'].encode('utf-8')))

    #         weapon_list_rank4.append(idx)
    #         if weapon_base_rank5_idx:
    #             if len(weapon_list_rank4) == 4:
    #                 self.logger.info(u'開始鍊金 -  5星*1 + 4星*4')
    #                 weapon_list_rank4.append(weapon_base_rank5_idx)
    #                 ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank4)
    #                 weapon_list_rank4[:] = []
    #                 # pprint.pprint(ret)
    #                 idx = ret['body'][1]['data'][0]['idx']
    #                 item_id = ret['body'][1]['data'][0]['id']
    #                 weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
    #                 # print idx, item_id
    #                 if int(item_id) in [85200, 26011]:
    #                     self.logger.info('!!! 得到神器 !!! {0}'.format(weapon_list[0]['name'].encode('utf-8')))
    #                     weapon_base_rank5_idx = None
    #                 else:
    #                     weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
    #                     self.logger.info('得到武器 {0}'.format(weapon_list[0]['name'].encode('utf-8')))
    #                     weapon_base_rank5_idx = idx
    #             else:
    #                 # print u'四星卡不足', len(weapon_list_rank4)
    #                 pass
    #         else:
    #             if len(weapon_list_rank4) == 5:
    #                 self.logger.info(u'開始鍊金 -  4星*5')
    #                 ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank4)
    #                 weapon_list_rank4[:] = []
    #                 # pprint.pprint(ret)
    #                 idx = ret['body'][1]['data'][0]['idx']
    #                 item_id = ret['body'][1]['data'][0]['id']
    #                 weapon_base_rank5_idx = idx

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
            gacha_info['area'] = self.config.getint(section, 'Area')
        except:
            gacha_info['area'] = None

        try:
            gacha_info['place'] = self.config.getint(section, 'Place')
        except:
            gacha_info['place'] = None

        try:
            gacha_info['auto_sell'] = self.config.getint(section, 'AutoSell')
        except :
            gacha_info['auto_sell'] = 0

        try:
            gacha_info['verbose'] = self.config.getint(section, 'Verbose')
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
        import  threading

        monitor_period = 30 # display money in every 30 seconds
        money_threshold = 1500000000
        def run(i):
            # print i
            card_idx_pool = [358771956, 330984563, 364031956]
            parameter = dict()
            parameter['explorer_idx'] = i + 1
            parameter['location_id'] = i
            parameter['card_idx'] = card_idx_pool[i]
            counter = 0
            parameter['pickup'] = 0

            while True:
                try:
                    r = explorer_client.cancel_explorer(parameter, self.account_info['sid'])
                    r = explorer_client.start_explorer(parameter, self.account_info['sid'])
                    if r['res'] == 0:
                        counter += 1
                    elif r['res'] == 2311:
                        parameter['pickup'] = 1
                    elif r['res'] == -2001:
                        # now processing
                        pass
                    elif r['res'] == 2304:
                        # is used explorer_idx, maybe too fask
                        pass
                    else:
                        self.logger.debug('Thread-{0} is breaking on unknown result: {1}'.format(i, r))
                        break
                except Exception as e:
                    self.logger.debug('Thread-{0} is breaking on exception: {1}'.format(i, e))
                    print e
                    break

        threads = []
        for i in range(0, 3):
            threads.append(threading.Thread(target=run, args=[i]))

        self.logger.debug('Threads start!')
        for t in threads:
            t.setDaemon(True)
            t.start()

        while True:
            r = alldata_client.get_alldata(self.account_info['sid'])
            data = r['body'][8]['data']
            for d in data:
                if d['item_id'] == 10:
                    if d['cnt'] <= money_threshold:
                        # BAD practice
                        sys.exit(0)
                    self.logger.slack("剩餘金幣 = {0}".format(d['cnt']))
                    money_current = d['cnt']
            time.sleep(monitor_period)



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
            gacha_result = self.do_gacha(gacha_info['gacha_type'], **gacha_info)
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
                        if card['rarity'] == 5:
                            self.logger.slack(msg)
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
        parameter['use_cnt'] = 1
        ret = None
        for i in range(0, 10):
            ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
            if ret['res'] != 0:
                parameter['item_id'] = 1
                ret = recovery_client.recovery_ap(parameter, self.account_info['sid'])
                return ret
        return ret

    def do_gacha(self, g_type, **kwargs):
        gacha_result = dict()
        parameter = dict()
        parameter['type'] = g_type
        for k, v in kwargs.iteritems():
            parameter[k] = v
        r = gacha_client.gacha(parameter, self.account_info['sid'])
        # print simplejson.dumps(r, ensure_ascii=False).encode('utf-8')

        if r['res'] == 0:
            for record in r['body']:
                # 新卡和舊卡位置不同，且新卡的位置也不固定
                try:
                    tmp = dict()
                    idx = record['data'][0]['idx']
                    cid = record['data'][0]['id']
                    tmp[idx] = cid
                    gacha_result[idx] = cid
                except Exception as e:
                    continue
            # print gacha_result


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
        self.do_present_process(1, 0, 'stone')

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
        url = 'http://v272.cc.mobimon.com.tw/card/sell'
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

    def __get_latest_quest(self):
        r = alldata_client.get_alldata(self.account_info['sid'])
        try:
            data = r['body'][1]['data'][-1]
            qtype = data['type']
            qid = data['id']
            lv = r['body'][4]['data']['lv']
            return qtype, qid, lv
        except Exception as e:
            self.logger.error(e)
            return None

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
    cc.set_proxy()
    cc.start()

if __name__ == '__main__':
    main()


#!/usr/bin/env python
#-*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
import time
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
import utils.response_parser
import utils.global_config
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
from lib import session_client
from lib import card_client
from lib import general_client
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
            'SIMPLE_COMPOSE': self.do_compose_simple,
            'TUTORIAL': self.do_pass_tutorial,
            'DRAMA': self.do_play_drama_auto,
            'TEACHER': self.do_teacher_section,
            'DISCIPLE': self.do_disciple_section,
            'DEBUG': self.do_debug_section,
            'SHOW_GACHA_EVENT': self.do_show_gacha_event,
            'UZU': self.do_uzu_section,
            'INFO_UZU': self.do_uzu_info_section,
            'RESET_DISCIPLE': self.do_reset_disciple,
            # 'AUTO_COMPOSE': self.do_auto_compose
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

                    try:
                        self.flow_loop = self.config.getint(section, 'FlowLoop')
                    except:
                        self.flow_loop = 1

                    try:
                        self.flow_loop_delay = self.config.getint(section, 'FlowLoopDelay')
                    except:
                        self.flow_loop_delay = 0

    def set_proxy(self):
        try:
            # self.logger.debug('Use socks5 proxy')
            socks_info = self.config.get('GLOBAL', 'Socks5')
            # print socks_info.split(':')
            [socks5_addr, socks5_port] = socks_info.split(':')
            socks.set_default_proxy(socks.SOCKS5, socks5_addr, int(socks5_port))
            socket.socket = socks.socksocket
        except Exception as e:
            pass
            # self.logger.warning('Not use proxy: {0}'.format(e))


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
                self.do_action(self.action_list[action_idx].upper())
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

    def do_login(self, uid=None):
        if uid:
            self.account_info['uid'] = uid

        ret = session_client.login(self.account_info['uid'], self.account_info['token'])
        # utils.response_parser.dump_response(ret)

        # print simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
        # sys.exit(0)
        try:
            self.account_info['sid'] = ret['login']['sid']
            # self.logger.debug('sid = {0}'.format(ret['login']['sid']))
            sid_file = '.' + os.path.basename(os.path.splitext(self.config_file)[0])
            with open(sid_file, 'w') as f:
                f.write(self.account_info['sid'])

        except KeyError:
            msg = u"無法登入, Message = {0}".format(ret['msg'])
            self.logger.error(msg)
            raise KeyError(msg)

    def __auto_compose(self, base_card_idx, max_lv):
        # Get all 成長卡
        card_list = alldata_client.get_allcards(self.account_info['sid'])
        mt_list = list()
        for c in card_list:
            if c['type'] == 3:
                mt_list.append(str(c['idx']))
        # print mt_list
        if not len(mt_list):
            self.logger.warning('No material to compose')
            raise Exception('No material to compose')

        def chunker(seq, size):
            return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

        for sub_mt in chunker(mt_list, 5):
            # print 'submt = {0}'.format(sub_mt)
            if not len(sub_mt):
                self.logger.warning('No material to compose')
                raise Exception('No material to compose')
            ret = card_client.compose(self.account_info['sid'], base_card_idx, sub_mt)
            lv = ret['body'][1]['data'][0]['lv']
            # utils.response_parser.dump_response(ret)
            if lv >= max_lv:
                self.logger.debug('Upgrade is completed')
                break
            self.logger.debug('Current LV {0}'.format(ret['body'][1]['data'][0]['lv']))

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
                self.logger.debug('UID {0} 給與 Rank {1} 獎勵, res= {2}'.format(self.account_info['uid'], i, r['res']))
                if r['res'] != 0:
                    self.logger.warning('UID {0} 無法給與 Rank {1} 獎勵, msg = {2}'.format(
                        self.account_info['uid'], tid, r))

            # r = teacher_disciple_client.reset_from_disciple(self.account_info['sid'])
            # print r
            #self.logger.debug('UID {0} reset from disciple {1}'.format(self.account_info['uid'], r['res']))

            r = teacher_disciple_client.thanks_thanks_graduate(self.account_info['sid'])
            if r['res'] == 0:
                self.logger.debug('徒弟畢業! UID = {0}'.format(self.account_info['uid'], r['res']))
                teacher_disciple_client.IS_DISCIPLE_GRADUATED = False
            else:
                self.logger.debug('徒弟 UID {0} 無法畢業, msg = {1}'.format(self.account_info['uid'], r))
        else:
            # 徒：申請師父
            r = teacher_disciple_client.apply_teacher(self.account_info['sid'], tid=tid)
            self.logger.debug('UID {0} 選擇 {1} 為師父, res = {2}'.format(self.account_info['uid'], tid, r['res']))
            if r['res'] != 0:
                self.logger.debug('選擇師父失敗: {0}'.format(r))
                raise Exception('Applay teacher failed!')

    def do_show_gacha_event(self, section, *args, **kwargs):
        import subprocess
        print subprocess.Popen("cd scripts && sh get_gacha_info.sh", shell=True, stdout=subprocess.PIPE).stdout.read()

    def do_reset_disciple(self, section, *args, **kwars):
        api_path = '/teacher/confirm_disciple'
        ret = general_client.general_post(self.account_info['sid'], api_path)
        disciple_info = ret['body'][0]['data']
        for disciple in disciple_info:
            if disciple['resetable']:
                self.logger.debug('Resetable student = {0}'.format(disciple['uid']))
                reset_api = '/teacher/reset_from_teacher'
                options = {'did': disciple['uid']}
                ret = general_client.general_post(self.account_info['sid'], reset_api, **options)
                self.logger.debug(ret)

    def do_uzu_info_section(self, section, *args, **kwars):
        import time
        ts = int(time.time())
        uzu_info_api = '/data/uzuinfo'
        ret = general_client.general_post(self.account_info['sid'], uzu_info_api)
        uzu_data_list = ret['uzu']

        # alldata = alldata_client.get_alldata(self.account_info['sid'])
        # uzu_info_list = alldata['body'][25]['data']
        # utils.response_parser.dump_response(alldata)
        # print uzu_info_list
        # for uzu_info in uzu_info_list:
        #     print uzu_info['uzu_id']
        #     print uzu_info['clear_list']

        for idx, uzu_data in enumerate(uzu_data_list):
            print '================='
            # cleared_list = uzu_info_list[idx]['clear_list']
            for sc in uzu_data['schedule']:
                if sc['start'] <= ts <= sc['end']:
                    current_scid = sc['schedule_id']
                    break
            print u'UZU Name = {0}, uzu_id = {1}, sc_id = {2}'.format(
                uzu_data['name'], uzu_data['uzu_id'], current_scid)
            # print u'Cleared List = {0}'.format(cleared_list)

            # print simplejson.dumps(uzu_data, ensure_ascii=False).encode('utf-8')


    def do_uzu_section(self, section, *args, **kwars):
        max_st = 12
        uzu_api = {
            'entry': '/uzu/entry',
            'result': '/uzu/result'
        }

        options_entry = dict()
        options_entry['uzid'] = self.config.get(section, 'uzid')
        options_entry['scid'] = self.config.get(section, 'scid')
        options_entry['fid'] = 1965350
        options_entry['htype'] = 0
        try:
            options_entry['st'] = self.config.getint(section, 'st')
        except Exception as e:
            options_entry['st'] = max_st
        options_entry['pt'] = self.config.get(section, 'pt')

        options_result = dict()
        options_result['res'] = 1
        options_result['uzid'] = self.config.get(section, 'uzid')

        # ret = general_client.general_post(self.account_info['sid'], '/data/uzuinfo')
        # utils.response_parser.dump_response(ret)
        for i in xrange(options_entry['st'], 0, -1):
            options_entry['st'] = i
            self.logger.debug(u'天魔挑戰開始, ID = {0}, 層數 = {1}'.format(options_entry['uzid'], options_entry['st']))
            ret = general_client.general_post(self.account_info['sid'], uzu_api['entry'], **options_entry)
            # self.logger.debug(ret['res'])
            # utils.response_parser.dump_response(ret)
            if ret['res'] == 0:
                self.logger.debug(u'挑戰天魔樓層 = {0}'.format(i))
                break
            elif ret['res'] == 2803:
                self.logger.warning(u'天魔挑戰權不足')
                return
            else:
                self.logger.warning(u'天魔層數: {0} 進入失敗: {1}'.format(i, ret['msg']))

        ret = general_client.general_post(self.account_info['sid'], uzu_api['result'], **options_result)
        if ret['res'] == 0:
            add_point = ret['uzu_result']['add_point']
            self.logger.debug(u'天魔挑戰成功，目前層數 = {0}，獲得點數 = {1}'.format(options_entry['st'], add_point))
        else:
            self.logger.debug(u'天魔挑戰失敗')
            utils.response_parser.dump_response(ret)


    def do_debug_section(self, section, *args, **kwargs):
        options = dict(self.config.items(section))
        options_global = dict(self.config.items("GLOBAL"))
        for k in options.keys():
            if k in options_global.keys():
                options.pop(k)

        api_path = options.pop('API')
        r = debug_client.debug_post(self.account_info['sid'], api_path, **options)
        # print r
        data = simplejson.dumps(r, ensure_ascii=False).encode('utf-8')
        print data

    def do_play_drama_auto(self, section, *args, **kwargs):
        quest_info = dict()
        results = list()
        parameter = dict()
        parameter['type'] = 1 # 體果
        parameter['item_id'] = 1
        parameter['use_cnt'] = 1
        lv_threshold = 50
        current_lv = 1
        max_retry_cnt = 10
        current_retry_cnt = 0
        self.logger.debug(u'開始通過主線任務...')
        while True:
            qtype, qid, lv = self.__get_latest_quest()
            if lv >= lv_threshold:
                self.logger.debug(u'等級達到門檻，停止主線任務'.format(lv_threshold))
                teacher_disciple_client.IS_DISCIPLE_GRADUATED = True
                break
            else:
                if lv != current_lv:
                    self.logger.debug(u'等級 = {0}'.format(lv))
                    pass
                current_lv = lv
            # self.logger.debug(u'下一個關卡為: {0},{1}'.format(qtype, qid))
            results[:] = []
            quest_info['qtype'] = qtype
            quest_info['qid'] = qid
            quest_info['fid'] = 1965350

            # workaround, 從response中無法判斷qtype為5的quest是寶物或是戰鬥，只好都試試看
            result = quest_client.start_quest(quest_info, self.account_info['sid'])
            rc_quest_entry = int(result['res'])
            results.append(rc_quest_entry)
            # self.logger.debug(rc_quest_entry)

            if rc_quest_entry == 0:
                result = quest_client.finish_quest(quest_info, self.account_info['sid'])
                rc_quest_finish = int(result['res'])
                results.append(rc_quest_finish)
                # self.logger.debug(rc_quest_finish)
            elif rc_quest_entry == 103:
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
                        self.logger.error('Unable to recover stamina, break')
                        break
            else:
                result = quest_client.get_treasure(quest_info, self.account_info['sid'])
                rc = int(result['res'])
                results.append(rc)
                # self.logger.debug(rc)

            # self.do_get_present('PRESENT')
            # Unknown error, retry can solve it
            if 0 not in results:
                # 主線可能會失敗，原因不明，會造成產生無法畢業的幽靈徒弟，會讓師父佔一個位置，重試一次可解決
                # Unknown error in drama [502, -501, 2]
                self.logger.error('Unknown error in drama {0}'.format(results))
                current_retry_cnt += 1
                if current_retry_cnt > max_retry_cnt:
                    self.logger.error(
                        'UID:{0} reaches max retry count but cannot finish drama, force break drama,\
                         please manually finish drama and make the disciple gradudate'.format(self.account_info['uid']))
                    break
                else:
                    self.logger.debug('Something wrong, retry...')
                    continue
            else:
                current_retry_cnt = 0


    def do_pass_tutorial(self, section, *args, **kwargs):
        import uuid
        # tutorial_count = self.config.getint(section, 'Count')
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
        # for i in range(0, tutorial_count):
        # self.account_info['uid'] = '{0}{1}'.format('test', str(uuid.uuid4()))
        account_uuid =  ''.join(['ANDO', str(uuid.uuid4())])
        self.config.set('GENERAL', 'Uid', account_uuid)
        self.account_info['uid'] = account_uuid
        self.do_login()

        # self.logger.debug(u'{0}/{1} - 開始新帳號'.format(i+1, tutorial_count))
        r = alldata_client.get_alldata(self.account_info['sid'])
        open_id = r['body'][4]['data']['uid']
        self.logger.debug(u'新帳號創立成功，UID = {0}, OpenID = {1}'.format(self.account_info['uid'], open_id))
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
        # r = alldata_client.get_alldata(self.account_info['sid'])
        # open_id = r['body'][4]['data']['uid']
        # 一定要留open id，這樣才容易反查徒弟的 uid，不然很難找到師徒對應關係，並且取消/繼續
        self.logger.debug(u'新帳號完成新手教學，UID = {0}, OpenID = {1}'.format(self.account_info['uid'], open_id))
        self.do_get_present('PRESENT')

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
        # self.do_compose()

    def do_show_status(self, section, *args, **kwargs):
        accepted_keys = ['uid', 'heroName', 'open_id', 'lv', 'cardMax', 'accept_disciple', 'name', 'friendCnt'
        'only_friend_disciple', 'staminaMax']
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
        stone_count = r['body'][12]['data']
        # logger.info(json.dumps(data_list, sort_keys=True, indent=2))
        for data in data_list:
            try:
                self.logger.debug("{0} = {1}".format(item_mapping[data['item_id']], data['cnt']))
            except KeyError:
                pass
        self.logger.debug(u'精靈石 = {0}'.format(stone_count))

        user_info = r['body'][4]['data']
        for key, data in user_info.iteritems():
            if key in accepted_keys:
                self.logger.debug(u"{0} = {1}".format(key, data))

    def do_show_all_cards(self, section, *args, **kwargs):
        """ 只列出四星/五星角色卡 """
        r = alldata_client.get_alldata(self.account_info['sid'])
        card_list = r['body'][6]['data']
        try:
            auto_compose = self.config.getboolean(section, 'AutoCompose')
        except:
            auto_compose = False

        try:
            rank_threshold = self.config.getint(section, 'RankThreshold')
        except:
            rank_threshold = 4
        # logger.info(json.dumps(data_list, sort_keys=True, indent=2))
        for card in card_list:
            if card['type'] != 0:  # not character card
                continue
            try:
                if auto_compose and card['lv'] == card['maxlv']:
                    continue
                cid = int(card['id'])
                card_dict = utils.db_operator.DBOperator.get_cards('cid', cid)[0]
                if card_dict and card_dict['rarity'] >= rank_threshold:
                    self.logger.debug(u"{0}-{1}, 界限突破：{2}, 等級: {3}/{4}, 稀有度: {5}, ID: {6}, IDX: {7}".format(
                        card_dict['title'], card_dict['name'], card['limit_break'], card['lv'],
                        card['maxlv'], card_dict['rarity'], cid, card['idx']))
                    if auto_compose:
                        self.logger.debug(u'Start to upgrade Card {0}'.format(card_dict['name']))
                        self.__auto_compose(card['idx'], card['maxlv'])

                    # self.logger.debug(int(card['idx']))
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
        try:
            quest_info['raid_recovery'] = self.config.getint(section, 'AutoRaidRecover')
        except:
            quest_info['raid_recovery'] = 0
        quest_info['fid'] = self.config.getint(section, 'Fid')
        quest_info['retry_interval'] = self.config.getint(section, 'RetryDuration')
        quest_info['max_event_point'] = self.config.getint(section, 'MaxEventPoint')
        quest_info['auto_sell'] = self.config.getint(section, 'AutoSell')
        try:
            quest_info['show_treasure'] = self.config.getint(section, 'ShowTreasure')
        except:
            quest_info['show_treasure'] = 0
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
            # utils.response_parser.dump_response(result)
            if quest_info['show_treasure']:
                treasure_list = result['earns']['treasure']
                for t in treasure_list:
                    # print t['type'], t['id']
                    try:
                        self.__dump_treasure_info(t['type'], t['id'])
                    except:
                        self.logger.debug(u'{0}, {1}, {2}'.format(t['type'], t['id'], t['val']))

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
                    print simplejson.dumps(result, ensure_ascii=False).encode('utf-8')
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
                self.do_raid_quest(fid=quest_info['fid'], auto_recover_bp=quest_info['raid_recovery'], auto_sell=quest_info['auto_sell'])

    def __dump_treasure_info(self, t_type, t_id):
        mapping = {
            'chara_rf': 'chararein',
            'weapon_rf': 'reinforce'
        }
        res = utils.db_operator.DBOperator.get_general(mapping[t_type], 'id', t_id)
        for r in res:
            self.logger.debug(r['name'])

    def do_raid_quest(self, **kwargs):
        boss_id = raid_client.get_raid_info(self.account_info['sid'], 'id')
        boss_lv = raid_client.get_raid_info(self.account_info['sid'], 'lv')
        # ret = raid_client.get_raid_info(self.account_info['sid'])
        # data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
        # print data
        if boss_id:
            parameter = dict()
            parameter['boss_id'] = boss_id
            # parameter['fid'] = '1965350'
            parameter['fid'] = kwargs['fid']
            auto_recover_bp = kwargs['auto_recover_bp']
            self.logger.debug(u"魔神來襲！魔神等級: [{0}]".format(boss_lv))
            r = raid_client.start_raid_quest(parameter, self.account_info['sid'])
            if r['res'] == 0:
                ret = raid_client.finish_raid_quest(parameter, self.account_info['sid'])
                ret2 = raid_client.get_raid_bonus(parameter, self.account_info['sid'])
                data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
                print data
                data = simplejson.dumps(ret2, ensure_ascii=False).encode('utf-8')
                print data
                earned_idx = None
                if boss_lv > 0:
                    data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
                    # print data
                    earned_idx = ret['body'][1]['data'][0]['idx']
                else:
                    self.logger.debug(u'爆走魔神獎勵')
                    try:
                        data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
                        # print data
                        earned_idx = ret2['body'][0]['data'][0]['idx']
                    except Exception as e:
                        pass

                if kwargs['auto_sell'] == 1 and earned_idx:
                    r = self.do_sell_item(earned_idx)
                    if r['res'] == 0:
                        self.logger.debug(u"\t-> 賣出卡片 {0}, result = {1}".format(earned_idx, r['res']))
                    else:
                        self.logger.error(u"\t-> 卡片無法賣出, Error Code = {0}".format(r['res']))
            elif r['res'] == 104:
                self.logger.debug(u"魔神戰體力不足")
                if auto_recover_bp:
                    self.logger.debug('Start to recovery BP')
                    ret = user_client.recover_bp(self.account_info['sid'], item_type=0, item_id=2)
                    if ret['res'] != 0:
                        self.logger.debug(ret)

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

    def do_compose_simple(self, section, *args, **kwargs):
        # 買某樣道具五次，直接鍊金
        # cnt=15b87000f0b&id=85313&kind=item&price=1&type=weapon_ev&val=1
        buy_count = 5
        target_weapon = list()
        target_weapon_keyword = list()
        count = self.config.getint(section, 'Count')
        try:
            eid = self.config.get(section, 'Eid')
        except:
            eid = None
        base_weapon_id = self.config.get(section, 'BaseWeaponID')
        weapon_data = {
            'kind': 'item',
            'type': 'weapon_ev',
            'id': base_weapon_id,
            'val': 1,
            'price': 1,
        }
        try:
            target_weapon_keyword_str = self.config.get(section, 'TargetsKeyWords')
            target_weapon_keyword = [i for i in target_weapon_keyword_str.split(',')]
        except Exception as e:
            pass

        for i in range(0, count):
            weapon_client_base = list()
            for j in range(0, buy_count):
                ret = item_client.buy_item(weapon_data, self.account_info['sid'])
                print ret
                data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
                base_weapon_idx = ret['body'][1]['data'][0]['idx']
                weapon_client_base.append(base_weapon_idx)

            ret = weapon_client.compose(self.account_info['sid'], weapon_client_base, eid)
            idx = ret['body'][1]['data'][0]['idx']
            item_id = ret['body'][1]['data'][0]['id']
            weapon_list = utils.db_operator.DBOperator.get_weapons('id', item_id)
            weapon_name = weapon_list[0]['name'].encode('utf-8')
            # print idx, item_id
            for keyword in target_weapon_keyword:
                b_found = False
                if keyword in weapon_name:
                    b_found = True
                    break
                else:
                    pass

            if b_found:
                self.logger.info('{0}/{1} - 鍊金完成，得到神器!!! {2}'.format(i, count, weapon_name))
            else:
                # self.logger.info('{0}/{1} - 鍊金完成，得到武器: {2}({3})'.format(i, count, weapon_name, item_id))
                r = self.do_sell_item(idx)




    def do_compose(self, section, *args, **kwargs):
        """
        以1張5星 +  3張4星鍊金
        """
        count = self.config.getint(section, 'Count')
        # target_weapon = list()
        try:
            eid = self.config.get(section, 'Eid')
        except:
            eid = None
        base_weapon_id = self.config.get(section, 'BaseWeaponID')
        weapon_data = {
            'kind': 'item',
            'type': 'weapon_ev',
            'id': base_weapon_id,
            'val': 1,
            'price': 10,
        }
        # target_weapon_str = self.config.get(section, 'Targets')
        # if target_weapon_str:
        #     target_weapon = [i for i in target_weapon_str.split(',')]

        weapon_list_rank3 = list()
        weapon_list_rank4 = list()
        # weapon_list_rank5 = list()
        weapon_base_rank5_idx = None # 基底武器

        try:
            target_weapon_keyword_str = self.config.get(section, 'TargetsKeyWords')
            target_weapon_keyword = [i for i in target_weapon_keyword_str.split(',')]
        except Exception as e:
            pass

        for i in range(0, count):
            # 沒有5星武器時，先鍊出一把五星武器
            buy_count = 5
            if weapon_base_rank5_idx:
                buy_count = 4
            # 買三星武器
            for j in range(0, buy_count):
                # ret = item_client.buy_item_with_type(item_type, self.account_info['sid'])
                ret = item_client.buy_item(weapon_data, self.account_info['sid'])
                data = simplejson.dumps(ret, ensure_ascii=False).encode('utf-8')
                base_weapon_idx = ret['body'][1]['data'][0]['idx']
                weapon_list_rank3.append(base_weapon_idx)

            # 五把三星器武器，鍊成四星武器
            if len(weapon_list_rank3) == 5:
                # self.logger.info(u'開始鍊金 -  3星*5')
                # self.logger.debug(weapon_list_rank3)
                ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank3, eid)
                weapon_list_rank3[:] = []
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
                ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank3, eid)
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
                weapon_name = weapon_list[0]['name'].encode('utf-8')

                for keyword in target_weapon_keyword:
                    b_found = False
                    if keyword in weapon_name:
                        b_found = True
                        break
                    else:
                        pass
                # print idx, item_id
                # if target_weapon and str(item_id) in target_weapon:
                if b_found:
                    self.logger.info('{0}/{1} - 鍊金完成，得到神器!!! {2}'.format(i, count, weapon_name))
                    weapon_base_rank5_idx = None
                    break
                else:
                    self.logger.info('{0}/{1} - 鍊金完成，得到武器: {2}'.format(i, count, weapon_name))
                    weapon_base_rank5_idx = idx

            # 鍊出做為基底的五星武器
            elif len(weapon_list_rank4) == 5:
                    # self.logger.info(u'開始鍊金 -  4星*5')
                    ret = weapon_client.compose(self.account_info['sid'], weapon_list_rank4, eid)
                    weapon_list_rank4[:] = []
                    # pprint.pprint(ret)
                    idx = ret['body'][1]['data'][0]['idx']
                    item_id = ret['body'][1]['data'][0]['id']
                    weapon_base_rank5_idx = idx

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
            gacha_info['auto_sell_rarity_threshold'] = self.config.getint(section, 'AutoSellRarityThreshold')
        except :
            gacha_info['auto_sell_rarity_threshold'] = 0

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
                    self.logger.debug("剩餘金幣 = {0}".format(d['cnt']))
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
        # self.logger.debug(simplejson.dumps(pickup_list, ensure_ascii=False))

        explorer_area = self.config.getlist(section, 'area')
        print explorer_area

        # debug section
        # card_idx = self.find_best_idx_to_explorer(pickup_list[3], except_card_id)
        # print card_idx
        #sys.exit(0)
        # for i in range(0, 3):

        #     parameter = {'explorer_idx': i+1}
        #     explorer_client.cancel_explorer(parameter, self.account_info['sid'])
        # sys.exit(0)

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
            for pickup_item in pickup_list:
                if pickup_item['location_id'] == area:
                    card_idx, card_id = self.find_best_idx_to_explorer(pickup_item, except_card_id)
                    except_card_id.append(card_id)
                    self.logger.debug('Explorer cards = {0}'.format(card_id))
                    break

            # go to explorer
            parameter = dict()
            parameter['explorer_idx'] = i+1
            parameter['location_id'] = area
            parameter['card_idx'] = card_idx
            parameter['pickup'] = 1

            try:
                parameter['interval'] = self.config.getint(section, 'interval')
            except:
                parameter['interval'] = 1

            try:
                stone_finish = self.config.getint(section, 'StoneFinish')
            except:
                stone_finish = 1

            r = explorer_client.start_explorer(parameter, self.account_info['sid'])
            if r['res'] == 2311:
                # self.logger.debug(u"pickup value error, retry")
                parameter['pickup'] = 0
                explorer_client.start_explorer(parameter, self.account_info['sid'])


            if stone_finish:
                # self.logger.debug('Use stone to finish explorer right now!')
                r = explorer_client.finish_explorer(parameter, self.account_info['sid'])
                # utils.response_parser.dump_response(r)

                r = explorer_client.get_explorer_result(parameter['explorer_idx'], self.account_info['sid'])
                for reward in r['explorer_reward']:
                    item_type = reward['item_type']
                    item_id = reward['item_id']
                    # self.logger.debug('==========================================')
                    # self.logger.debug('Reward Type: {0}'.format(item_type))
                    if item_type == 'card':
                        card = utils.db_operator.DBOperator.get_cards('cid', item_id)[0]
                        self.logger.debug('得到角色: {0}'.format(card['name'].encode('utf-8')))
                    else:
                        pass
                        # self.logger.debug('Reward ID: {0}'.format(item_id))
                    # self.logger.debug('Reward Val: {0}'.format(reward['item_val']))
                # utils.response_parser.dump_response(r, key='explorer_reward')



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
        # for i in xrange(0, gacha_info['count']):
            # if gacha_info['gacha_type'] in [3, 8]:
                # time.sleep(3)
        sell_candidate = list()
        self.logger.info(u"轉蛋開始！")
        gacha_result = self.do_gacha(gacha_info['gacha_type'], **gacha_info)
        self.logger.debug(u"得到卡片: {0}".format(gacha_result.values()))
        if gacha_info['verbose']:
            cids = gacha_result.values()
            for cidx, cid in gacha_result.iteritems():
            # for cid in cids:
                cards = utils.db_operator.DBOperator.get_cards('cid', cid)
                # if not cards or 'name' not in cards[0] or 'rarity' not in cards[0]:
                # use BIF all() to check if the dict has key 'name' AND 'rarity'
                if not cards or not all([i in cards[0].keys() for i in ['name', 'rarity', 'title']]):
                    self.logger.debug(cid)
                else:
                    card = cards[0]  # cid is key index
                    if card['rarity'] >= gacha_info['auto_sell_rarity_threshold']:
                        msg = '得到 {0}-{1}, 稀有度: {2}'.format(card['title'].encode('utf-8'), card['name'].encode('utf-8'), card['rarity'])
                        self.logger.debug(msg)
                    else:
                        pass

                    if card['rarity'] < gacha_info['auto_sell_rarity_threshold']:
                        sell_candidate.append([cidx, card['name']])

                    #     self.logger.debug(msg)
                    #self.logger.debug(msg)

        #if gacha_result is None or len(gacha_result) == 0:
        if not gacha_result:
            self.logger.debug("Gacha Error")
            raise Exception('Gacha Error')

        if gacha_info['auto_sell_rarity_threshold']:
            self.logger.info('開始賣出稀有度{0}(含) 以下的卡片...'.format(gacha_info['auto_sell_rarity_threshold']-1))
            for candidate in sell_candidate:
                cidx = candidate[0]
                c_name = candidate[1]
                ret = self.do_sell_item(cidx)
                '''
                if ret['res'] == 0:
                    self.logger.debug(u"賣出 {0} 成功".format(c_name))
                else:
                    self.logger.debug(u"賣出 {0} 失敗".format(c_name))
                '''

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
                    for data in record['data']:
                        tmp = dict()
                        idx = data['idx']
                        cid = data['id']
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
        # self.logger.debug('禮物清單: {0}'.format(present_ids))
        while len(present_ids) > 0:
            pid = present_ids.pop(0)
            # self.logger.debug("接收禮物 {0}".format(pid))
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
        url = '{0}/card/sell'.format(utils.global_config.get_hostname())
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

        # self.logger.debug("Pickup attribute home: {0}".format(area_pickup_list['home']))
        # self.logger.debug("Pickup attribute job type: {0}".format(area_pickup_list['jobtype']))
        # self.logger.debug("Pickup attribute weapontype: {0}".format(area_pickup_list['weapontype']))
        temp_idx = None
        for card in card_list:
            if card['id'] in except_card_id:
                # self.logger.debug(u"跳過保留不去探索的卡片: {0}".format(card['id']))
                continue


            if card['type'] == 0:
                card_doc = None
                card_doc_list = utils.db_operator.DBOperator.get_cards('cid', card['id'])
                if len(card_doc_list) > 0:
                    card_doc = card_doc_list[0]
                if card_doc:
                    if 'rarity' in card_doc and card_doc['rarity'] >= 5:
                        continue
                    temp_idx = card['idx']

                    # self.logger.debug("home:{0}, {1}".format(card_doc['home'], type(card_doc['home'])))
                    # self.logger.debug("jobtype:{0}".format(card_doc['jobtype']))
                    # TODO: bug here, weapon type is not equal to battletype
                    # how to solve it due to mongodb has no weapon type record
                    # self.logger.debug("weapontype:{0}".format(card_doc['battletype']))
                    if (int(area_pickup_list['home']) == card_doc['home']) or (
                        int(area_pickup_list['jobtype']) == card_doc['jobtype']) or (
                        int(area_pickup_list['weapontype']) == card_doc['battletype']):

                        temp_idx = card['idx']
                        # self.logger.debug(u"Found pickup card! {0}".format(card_doc['name']))
                        # self.logger.debug(u"{0} is picked to eplorer".format(temp_idx))
                        self.logger.debug(u'Pick {0} to explorer'.format(card_doc['name']))
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
        try:
            event_point = result['body'][1]['data']['point']
        except Exception as e:
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

    for i in xrange(0, cc.flow_loop):
        cc.logger.debug('Start #{0}/{1} Flow'.format(i+1, cc.flow_loop))
        if args.action is not None:
            # force overwrite config flow and just do the action from args
            cc.action_list = [args.action]
        cc.set_proxy()
        cc.start()
        cc.logger.debug('End of #{0} Flow'.format(i+1, cc.flow_loop))
        if cc.flow_loop_delay > 0:
            cc.logger.debug('Sleeping {0} seconds'.format(cc.flow_loop_delay))
            time.sleep(cc.flow_loop_delay)


if __name__ == '__main__':
    main()


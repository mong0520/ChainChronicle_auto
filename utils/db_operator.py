# -*- coding: utf-8 -*
from tinydb import TinyDB, Query
import os
from os.path import expanduser
from . import poster
from pymongo import MongoClient

DB_PATH = expanduser('~/ChainChronicle/db/')
if not os.path.isdir(DB_PATH):
    os.makedirs(DB_PATH)
DB_SOURCE_BASE = 'http://v322.cc.mobimon.com.tw/data/'
data_mapping = {
    'evolve':{
        'db_source': DB_SOURCE_BASE + 'weaponlist',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'evolve')),
        'raw_list': list()
    },
    'weaponlist':{
        'db_source': DB_SOURCE_BASE + 'weaponlist',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'weaponlist')),
        'raw_list': list()
    }
    ,
    'charainfo': {
        'db_source': DB_SOURCE_BASE + 'charainfo',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'charainfo')),
        'raw_list': list()
    },
    'chararein': {
        'db_source': DB_SOURCE_BASE + 'charainfo',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'chararein')),
        'raw_list': list()
    },
    'questdigest': {
        'db_source': DB_SOURCE_BASE + 'questdigest',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'questdigest')),
        'raw_list': list()
    },
    'skilllist': {
        'db_source': DB_SOURCE_BASE + 'skilllist',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'skilllist')),
        'raw_list': list()
    }

    # note, weaponlist有三個資料可以拿，一個叫weaponlist，是一般武器，一個叫evolve，是鍊金武器，一個叫reinforce，是武器強化卡
    # weaponlist, skilllist, charainfo, questdigest, supportersskill, bossinfo, weaponcomposeevent, explorerlocation
}


class DBOperator(object):

    @staticmethod
    def __query(db, field, value):
        card = Query()
        if not field and not value:
            result_list = db.search(card.name.exists())
            # print result_list[0]
            return [result_list[0]]

        my_search = getattr(card, field)
        try:
            v = int(value)
            result_list = db.search(my_search == v)
        except ValueError:
            v = value
            name_keyword = '.?{0}.?'.format(v)
            result_list = db.search(my_search.search(name_keyword))

        return result_list

    @staticmethod
    def get_cards(field, value):
        """
        :param field: field to find, e.q,: title, name
        :param value: field value to match
        :return: matched dictionary
        """
        result_list = DBOperator.__query(
            data_mapping['charainfo']['db_obj'], field, value)
        return result_list

    @staticmethod
    def get_quests(quest_name):
        result_list = DBOperator.__query(
            data_mapping['questdigest']['db_obj'], field='name', value=quest_name)
        if result_list:
            return result_list
        else:
            return None

    @staticmethod
    def get_weapons(field, value):
        weapon_list = DBOperator.__query(
            data_mapping['evolve']['db_obj'], field, value)
        if weapon_list:
            return weapon_list
        else:
            return None

    @staticmethod
    def dump_cards(field, value):
        results = DBOperator.get_cards(field, value)
        target_fields = ['cid', 'title', 'name', 'profile', 'rarity']
        for r in results:
            print('===========================')
            for key in target_fields:
                try:
                    print('{0}: {1}'.format(key, r[key]))
                except UnicodeEncodeError:
                    print('{0}: {1}'.format(key, r[key].encode('utf-8')))
                except KeyError:
                    pass

    @staticmethod
    def dump_quest(quest_name, verbose=False):
        quests = DBOperator.get_quests(quest_name)
        if verbose:
            for quest in quests:
                print('===========================')
                for k, v in quest.items():
                    print('{0}: {1}'.format(k, v))
        else:
            for quest in quests:
                print('===========================')
                print('Chapter: {0}'.format(quest['chapter_cnt']))
                print('ID: {0}'.format(quest['quest_id']))
                print('Name: {0}'.format(quest['name'].encode('utf-8')))
                print('Difficult: {0}'.format(quest['difficulty']))


    @staticmethod
    def dump_weapon(field, value):
        weapons = DBOperator.get_weapons(field, value)
        for weapon in weapons:
            print('===========================')
            for k, v in weapon.items():
                print('{0}: {1}'.format(k, v))

    @staticmethod
    def dump_general(source, field, value):
        result_list = DBOperator.get_general(source, field, value)

        # ad-hoc logic to dump charainfo to avoid too many info
        if source == 'charainfo':
            DBOperator.dump_cards(field, value)
        else:
            for result in result_list:
                for k, v in result.items():
                    print('{0}: {1}'.format(k, v))
                print("===============================")


    @staticmethod
    def get_general(source, field, value):
        db_obj = TinyDB(os.path.join(DB_PATH, source))
        result_list = DBOperator.__query(db_obj, field, value)
        return result_list



class DBUpdater(object):

    @staticmethod
    def _initial_db_file(category):
        db_path = os.path.join(DB_PATH, category)
        if os.path.exists(db_path):
            print('Remove existence db file')
            os.unlink(db_path)
        data_mapping[category]['db_obj'] = TinyDB(db_path)

    

    @staticmethod
    def update_mongodb():
        client = MongoClient('127.0.0.1', 27017)
        db = client.cc
        # Get latest charainfo 
        for category in list(data_mapping.keys()):
            url = data_mapping[category]['db_source']
            print('Getting data from {0}'.format(url))
            r = poster.Poster.get_data(url)
            print('complete')

            print('remove existing data')
            try:
                getattr(db, category).remove({})
            except:
                print('unable to remove db.{0}'.format(category))

            # Insert latest data
            for element in r[category]:
                # print element
                if type(element) is list:
                    for doc in element:
                        collection = getattr(db, category).insert_one(doc)
                elif type(element) is dict:
                    collection = getattr(db, category).insert_one(element) 


    @staticmethod
    def update_tinydb():
        # Get latest charainfo data
        for category in list(data_mapping.keys()):
            url = data_mapping[category]['db_source']
            print('Getting data from {0}'.format(url))
            r = poster.Poster.get_data(url)
            print('complete')

            if len(r[category]) > 0:
                print('init db file')
                DBUpdater._initial_db_file(category)
            else:
                print('Unable to get DB information of category {0}'.format(category))

            # Insert latest data
            for element in r[category]:
                # print element
                if type(element) is list:
                    for doc in element:
                        data_mapping[category]['raw_list'].append(doc)
                elif type(element) is dict:
                    data_mapping[category]['raw_list'].append(element)

            # for data in data_mapping[category]['raw_list']:
            #     print data['id']
            data_mapping[category]['db_obj'].insert_multiple(data_mapping[category]['raw_list'])

if __name__ == '__main__':
    DBOperator.dump_cards('title', '狐尾')
    DBOperator.dump_cards('name', '菲娜')



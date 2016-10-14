# -*- coding: utf-8 -*
from tinydb import TinyDB, Query
import os
from os.path import expanduser
import poster

DB_PATH = expanduser('~/ChainChronicle/db/')
if not os.path.isdir(DB_PATH):
    os.makedirs(DB_PATH)
DB_SOURCE_BASE = 'http://v267b.cc.mobimon.com.tw/data/'
data_mapping = {
    'charainfo': {
        'db_source': DB_SOURCE_BASE + 'charainfo',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'charainfo')),
        'raw_list': list()
    },
    'questdigest': {
        'db_source': DB_SOURCE_BASE + 'questdigest',
        'db_obj': TinyDB(os.path.join(DB_PATH, 'questdigest')),
        'raw_list': list()
    }
}


class DBOperator(object):

    @staticmethod
    def __query(db, field, value):
        card = Query()
        my_search = getattr(card, field)
        try:
            v = int(value)
            result_list = db.search(my_search == v)
        except ValueError:
            v = value
            name_keyword = u'.?{0}.?'.format(v.decode("utf-8"))
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
    def dump_cards(field, value):
        results = DBOperator.get_cards(field, value)
        for r in results:
            # print r.keys()
            try:
                print '==========================='
                print 'ID: {0}'.format(r['cid'])
                print 'Title: {0}'.format(r['title'].encode('utf-8'))
                print 'Name: {0}'.format(r['name'].encode('utf-8'))
                # print 'Home: {0}'.format(r['home'])
                print 'Profile: {0}'.format(r['profile'].encode('utf-8'))
                print 'Rarity: {0}'.format(r['rarity'])
            except KeyError:
                pass

    @staticmethod
    def dump_quest(quest_name):
        quests = DBOperator.get_quests(quest_name)
        for quest in quests:
            print '==========================='
            print 'Chapter: {0}'.format(quest['chapter_cnt'])
            print 'ID: {0}'.format(quest['quest_id'])
            print 'Name: {0}'.format(quest['name'].encode('utf-8'))
            print 'Difficult: {0}'.format(quest['difficulty'])



class DBUpdater(object):

    @staticmethod
    def _initial_db_file(category):
        db_path = os.path.join(DB_PATH, category)
        if os.path.exists(db_path):
            print 'Remove existence db file'
            os.unlink(db_path)
        data_mapping[category]['db_obj'] = TinyDB(db_path)

    @staticmethod
    def update_db():
        # Get latest charainfo data
        for category in data_mapping.keys():
            url = data_mapping[category]['db_source']
            print 'Getting data from {0}'.format(url)
            r = poster.Poster.get_data(url)
            print 'complete'

            if len(r[category]) > 0:
                print 'init db file'
                DBUpdater._initial_db_file(category)
            else:
                print 'Unable to get DB information of category {0}'.format(category)

            # Insert latest data
            for element in r[category]:
                print element
                if type(element) is list:
                    for doc in element:
                        data_mapping[category]['raw_list'].append(doc)
                elif type(element) is dict:
                    data_mapping[category]['raw_list'].append(element)

            data_mapping[category]['db_obj'].insert_multiple(data_mapping[category]['raw_list'])

if __name__ == '__main__':
    DBOperator.dump_cards('title', '狐尾')
    DBOperator.dump_cards('name', '菲娜')



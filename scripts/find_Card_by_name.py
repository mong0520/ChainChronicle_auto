# -*- coding: utf-8 -*
import sys
from tinydb import TinyDB, where, Query
import simplejson as json
import argparse


def query(args):
    db = TinyDB('charainfo.db')
    card = Query()
    my_search = getattr(card, args.type)
    print 'start to query db'

    try:
        value = int(args.value)
        result_list = db.search(my_search == value)
    except ValueError:
        value = args.value
        name_keyword = u'.?{0}.?'.format(value.decode("utf-8"))
        result_list = db.search(my_search.search(name_keyword))

    for r in result_list:
        # print r.keys()
        print '==========================='
        print 'Name: {0}'.format(r['name'].encode('utf-8'))
        print 'ID: {0}'.format(r['cid'])
        print 'Title: {0}'.format(r['title'].encode('utf-8'))
        print 'Profile: {0}'.format(r['profile'].encode('utf-8'))
        print 'Rarity: {0}'.format(r['rarity'])
        print '==========================='
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-t', '--type', help='Card name', required=True, action='store')
    parser.add_argument('-v', '--value', help='value', required=True, action='store')
    args = parser.parse_args()
    query(args)
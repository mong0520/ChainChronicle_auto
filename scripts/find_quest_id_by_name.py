from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
#client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.quest

try:
    quest_doc = collection.find_one({"name": sys.argv[1]})
    print "Quest Type ID = %d" % quest_doc['place_id']
    print "Quest ID = %d" % quest_doc['quest_id']
    #print "Quest Name = %s" % quest_doc['name']
except Exception as e:
    print "no data"
    print e


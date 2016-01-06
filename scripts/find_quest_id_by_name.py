from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
#client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.quest

try:
    quest_doc = collection.find({"name": {"$regex": sys.argv[1]} })
    for doc in quest_doc:
        print "================================="
        print "Quest Type ID = %d" % doc['place_id']
        print "Quest ID = %d" % doc['quest_id']
        print "Quest Name = %s" % doc['name']
        print "================================="
except KeyError as e:
    print "Result doesn't include key [{0}]".format(e)
except Exception as e:
    raise


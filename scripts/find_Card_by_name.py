from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
#client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.charainfo

try:
    quest_doc = collection.find({"name": {"$regex": sys.argv[1]} })
    for doc in quest_doc:
        #print doc
        print doc['cid']
        print doc['name']
        print doc['_id']
except KeyError as e:
    print "Result doesn't include key [{0}]".format(e)
except Exception as e:
    raise


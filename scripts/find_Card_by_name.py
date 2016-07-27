from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
collection = client.cc.charainfo

try:
    quest_doc = collection.find({"name": {"$regex": sys.argv[1]} })
    for doc in quest_doc:
        #print doc
        print doc['cid']
        print "%s %s" % (doc['title'], doc['name'])
except KeyError as e:
    print "Result doesn't include key [{0}]".format(e)
except Exception as e:
    raise

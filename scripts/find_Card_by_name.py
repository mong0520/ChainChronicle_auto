from pymongo import MongoClient
import sys
import json

client = MongoClient('127.0.0.1', 27017)
collection = client.cc.charainfo

try:
    #quest_doc = collection.find({"name": {"$regex": sys.argv[1]} })
    quest_doc = collection.find({"name": {"$regex": sys.argv[1]} }, {"_id": 0})
    for doc in quest_doc:
        print json.dumps(doc, encoding="UTF-8", ensure_ascii=False)
        # print doc
        print doc['cid']
        print "%s %s" % (doc['title'], doc['name'])
except KeyError as e:
    print "Result doesn't include key [{0}]".format(e)
except Exception as e:
    raise

from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
#client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.charainfo

cid_doc = collection.find({})
print cid_doc
for doc in cid_doc:
    if 'cid' in doc:
        print "%s" % doc['cid']
    else:
        print doc

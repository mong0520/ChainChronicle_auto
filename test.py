from pymongo import MongoClient
client = MongoClient('127.0.0.1', 27017)
#client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.charainfo
try:
    cardName = collection.find_one({"cid": 7014})['name']
    print cardName
except Exception as e:
    print e


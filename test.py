from pymongo import MongoClient
client = MongoClient('lineage.twbbs.org', 27017)
client.the_database.authenticate('admin', 'mong730520', source = 'admin')
collection = client.cc.charainfo
cardName = collection.find_one({"cid": 7014})['name']
print cardName


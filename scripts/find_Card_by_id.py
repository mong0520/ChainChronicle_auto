from pymongo import MongoClient
import sys
client = MongoClient('127.0.0.1', 27017)
collection = client.cc.charainfo

def find_card_by_id(cid):
    try:
        quest_doc = collection.find({"cid": cid })
        if quest_doc:
            for doc in quest_doc:
                return doc
        else:
            return None
    except KeyError as e:
        raise
    except Exception as e:
        raise
    

if __name__ == '__main__':
    doc = find_card_by_id(int(sys.argv[1]))
    if doc:
        print doc['cid']
        print doc['name']



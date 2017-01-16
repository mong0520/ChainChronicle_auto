import simplejson


def dump_response(response_dict, key=None):
    if not key:
        data = simplejson.dumps(response_dict, ensure_ascii=False).encode('utf-8')
        print data, type(data)
    else:
        data = simplejson.dumps(response_dict[key], ensure_ascii=False).encode('utf-8')
        print data, type(data)
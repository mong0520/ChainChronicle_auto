import uuid

count = 1000000

for i in range(0, count):
    print "%s%s" % ('ANDO', str(uuid.uuid4()))



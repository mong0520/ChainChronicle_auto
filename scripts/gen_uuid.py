import uuid
import sys

count = int(sys.argv[1])

for i in range(0, count):
    print "%s%s" % ('ANDO', str(uuid.uuid4()))



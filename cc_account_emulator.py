from cc_main import ChainChronicle
import threading
import time
import sys
import logging
import traceback
import argparse


class CCAccountEmulator(threading.Thread):
    def __init__(self, config, uuid_list):
        threading.Thread.__init__(self)
        self.cc = ChainChronicle(config, console_log_level=logging.CRITICAL)
        self.cc.load_config()
        self.uuid_list = uuid_list
        self.counter = 0


    def run(self):
        while True:
            try:
                uuid = self.uuid_list[self.counter].strip()
                self.counter += 1
                self.cc.config.set('GENERAL', 'Uid', uuid)
                self.cc.account_info['uid'] = uuid
                print "Use uuid {0}".format(uuid)
                self.cc.start()
            except Exception as e:
                if self.counter >= len(self.uuid_list):
                    print 'reset uuid'
                    self.counter = 0
                else:
                    traceback.print_exc()  
                    print 'select next uuid'
                    self.counter += 1 


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Fake Account Emulator")
    parser.add_argument('-c', '--config', help='fake account template', required=True, action='store')
    parser.add_argument('-f', '--uuid_file', help='predefined uuid list', required=True, action='store')
    parser.add_argument('-t', '--thread', help='thread count', required=True, action='store', type=int)
    args = parser.parse_args()
  
    thread_count = args.thread
    threads = list()
    with open(args.uuid_file, 'r') as uuid:
        uuid_list = [u.strip() for u in uuid.readlines()]
    line_count = len(uuid_list)

    # seperate 1000000 lines to 2000 part, each part has 5000 items
    uuid_chunk_list = list(chunks(uuid_list, line_count / thread_count))
    # print len(uuid_chunk_list)
    # print len(uuid_chunk_list[0])
    # sys.exit(0)
    for i in xrange(0, thread_count):
        # threads.append(CCAccountEmulator('config/fake_account.conf', uuid_list))
        threads.append(CCAccountEmulator(args.config, uuid_chunk_list[i]))

    for t in threads:
        print 'Thread {0} starts'.format(t)
        t.start()

    for t in threads:
        print 'Main thread starts to waiting Thread: {0}'.format(t)
        t.join()

if __name__ == '__main__':
    main()


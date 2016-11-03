from cc_main import ChainChronicle
import threading
import time
import sys
import logging
import traceback
import argparse
try:
    import socket
    import socks
except:
    pass



class CCAccountEmulator(threading.Thread):
    def __init__(self, thread_id, config, uuid_list, target_ac_point, proxy=False):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.cc = ChainChronicle(config, console_log_level=logging.CRITICAL)
        self.cc.load_config()
        self.uuid_list = uuid_list
        self.counter = 0
        self.target_ac_point = target_ac_point
        if proxy:
            self.set_proxy()

    def set_proxy(self):
        socks5_addr = '127.0.0.1'
        socks5_port = 9050
        try:
            print 'Trying to set SOCKS5 Proxy'
            socks.set_default_proxy(socks.SOCKS5, socks5_addr, socks5_port)
            socket.socket = socks.socksocket
        except Exception as e:
            print e
            print 'Failed to set Socks5 proxy'
            sys.exit(0)


    def run(self):
        earned_ac_point = 0

        # not garuanteed the accuracy
        quest_count = self.cc.config.getint('QUEST', 'Count')
        ac_earn_in_batch = int(10 * quest_count)
        print 'Earned AC for one UUID in {0} counts: {1}'.format(quest_count, ac_earn_in_batch)

        while True:
            try:
                uuid = self.uuid_list[self.counter].strip()
                self.counter += 1
                self.cc.config.set('GENERAL', 'Uid', uuid)
                self.cc.account_info['uid'] = uuid
                print "Use uuid {0}".format(uuid)
                self.cc.start()
                earned_ac_point += ac_earn_in_batch
                if self.target_ac_point is not None:
                    if earned_ac_point >= self.target_ac_point:
                        print 'Thread:{0} earned AC point: {1}, Reach target AC point: {2}, mission is completed'.format(
                            self.thread_id, earned_ac_point, self.target_ac_point)
                        break
                    else:
                        print 'Thread:{0} earned AC point: {1}, target AC point: {2}'.format(
                            self.thread_id, earned_ac_point, self.target_ac_point)
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
    parser.add_argument('-p', '--ac_point', help='target AC point to earn', required=False, action='store', type=int,
                        default=None)
    args = parser.parse_args()

    target_ac = args.ac_point
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
    if target_ac and target_ac >= 0:
        target_ac_per_thread = args.ac_point / thread_count
    else:
        target_ac_per_thread = None

    print 'Target AC point = {0}, thread count = {1}, so each thread should earn at least {2} AC point'.format(
        args.ac_point, thread_count, target_ac_per_thread
    )

    for i in xrange(0, thread_count):
        # threads.append(CCAccountEmulator('config/fake_account.conf', uuid_list))
        threads.append(CCAccountEmulator(i, args.config, uuid_chunk_list[i], target_ac_per_thread, proxy=True))

    for t in threads:
        print 'Thread {0} starts'.format(t.thread_id)
        t.start()

    for t in threads:
        print 'Main thread starts to waiting Thread: {0}'.format(t.thread_id)
        t.join()

if __name__ == '__main__':
    main()


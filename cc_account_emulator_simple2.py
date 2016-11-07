from Queue import Queue
from threading import Thread
from cc_main import ChainChronicle
import threading
import time
import sys
import logging
import traceback
import argparse
import multiprocessing
try:
    import socket
    import socks
except:
    pass

uuid_queue = Queue(maxsize=0)
USE_PROXY = False


def _set_proxy():
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


def run(queue):
    if USE_PROXY:
        _set_proxy()
    while True:
        uuid = queue.get()
        # print "Use uuid {0}".format(uuid)
        try:
            config = 'config/fake_account.conf'
            cc = ChainChronicle(config, console_log_level=logging.CRITICAL)
            cc.load_config()
            cc.config.set('GENERAL', 'Uid', uuid)
            cc.account_info['uid'] = uuid
            print "UUID: {0} starts".format(uuid)
            cc.start()
            queue.task_done()
            print "UUID: {0} completes".format(uuid)
        except Exception as e:
            print e
            queue.task_done()
            print "### UUID: {0} failes ###".format(uuid)


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Fake Account Emulator")
    parser.add_argument('-f', '--uuid_file', help='predefined uuid list', required=True, action='store')
    parser.add_argument('-t', '--thread', help='thread count', required=True, action='store', type=int)
    args = parser.parse_args()
    thread_count = args.thread

    # Start workers
    print 'Starting {0} workers'.format(thread_count)
    for i in range(thread_count):
        worker = Thread(target=run, args=(uuid_queue,))
        worker.setDaemon(True)
        worker.start()

    print 'Starting to add UUIDs to task queue'
    with open(args.uuid_file, 'r') as uuid:
        for u in uuid.readlines():
            uuid_queue.put(u.strip())

    uuid_queue.join()


if __name__ == '__main__':
    main()
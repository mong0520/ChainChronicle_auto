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

USE_PROXY = True
CONFIG = 'config/fake_account.conf'
cc = ChainChronicle(CONFIG, console_log_level=logging.CRITICAL)
cc.load_config()


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


def run(uuid):
    if USE_PROXY:
        _set_proxy()
    while True:
        try:
            cc.config.set('GENERAL', 'Uid', uuid)
            cc.account_info['uid'] = uuid
            print "Use uuid {0}".format(uuid)
            cc.start()
            return
        except Exception as e:
            print e
            return


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Fake Account Emulator")
    parser.add_argument('-f', '--uuid_file', help='predefined uuid list', required=True, action='store')
    parser.add_argument('-t', '--thread', help='thread count', required=True, action='store', type=int)

    args = parser.parse_args()

    thread_count = args.thread
    with open(args.uuid_file, 'r') as uuid:
        uuid_list = [u.strip() for u in uuid.readlines()]

    t_pool = multiprocessing.Pool(thread_count)
    t_pool.map(run, uuid_list)
    t_pool.close()
    t_pool.join()


if __name__ == '__main__':
    main()


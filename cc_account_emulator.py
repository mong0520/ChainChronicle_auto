from cc_main import ChainChronicle
import uuid
import threading
import time

class CCAccountEmulator(threading.Thread):
    def __init__(self, config='config/fake_account.conf'):
        threading.Thread.__init__(self)
        self.cc = ChainChronicle(config)
        self.cc.load_config()
        self.overwrite_template_info()
                  
    def get_uuid(self):
        return "%s%s" % ('ANDO', str(uuid.uuid4()))

    def overwrite_template_info(self):
        uuid = self.get_uuid()
        self.cc.config.set('GENERAL', 'Uid', uuid)
        self.cc.config.set('QUEST', 'QuestId', '3,241902')
        self.cc.config.set('QUEST', 'Count', '10')
        self.cc.action_list = ['QUEST']
        self.cc.account_info['uid'] = uuid

    def run(self):
        self.cc.start()


if __name__ == '__main__':
    thread_count = 30
    threads = list()
    while True:
        del threads[:]
        for i in xrange(0, thread_count):
            threads.append(CCAccountEmulator())
    
        for t in threads:
            t.start()
    
        for t in threads:
            t.join()
    

import logging
from logging.handlers import RotatingFileHandler
import os
from pyslack import SlackHandler
import requests
requests.packages.urllib3.disable_warnings() # disable slack warning

# Slack integration for logger
LOG_LEVEL_SLACK = 60
logging.addLevelName(LOG_LEVEL_SLACK, "SLACK") # display name
def slack(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    self._log(LOG_LEVEL_SLACK, message, args, **kws)
logging.Logger.slack = slack

class CCLogger(object):

    __logger = None


    def __init__(self, tail_name='default', level=logging.DEBUG):
        if CCLogger.__logger:
            raise CCLogger.__logger
        file_formatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
                                           '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        console_formatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
                                              '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        slack_formatter = logging.Formatter('[%(asctime)s]: %(message)s', datefmt='%B %d %H:%M:%S')

        slack_api_key = 'xoxp-114030384193-115394422855-114791597460-f52b50029238196e449fb999feca4523'

        log_basepath = 'logs'
        if not os.path.exists(log_basepath):
            os.makedirs(log_basepath)

        CCLogger.__logger = logging.getLogger("Chain Chronicle")
        CCLogger.__logger.setLevel(logging.DEBUG)

        log_name = "{0}.log".format(tail_name)
        log_path = os.path.join(log_basepath, log_name)
        # 50 MB
        rh = RotatingFileHandler(log_path, maxBytes=1024 * 10000 * 5, backupCount=10)
        rh.setLevel(logging.DEBUG)
        rh.setFormatter(file_formatter)

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(console_formatter)

        handler = SlackHandler(slack_api_key, '#cc', username='botname')
        handler.setLevel(LOG_LEVEL_SLACK)
        handler.setFormatter(slack_formatter)


        if not CCLogger.__logger.handlers:
            CCLogger.__logger.addHandler(rh)
            CCLogger.__logger.addHandler(console)
            CCLogger.__logger.addHandler(handler)

    @staticmethod
    def get_logger(log_id, level):
        if CCLogger.__logger is None:
            CCLogger(log_id, level)
        return CCLogger.__logger



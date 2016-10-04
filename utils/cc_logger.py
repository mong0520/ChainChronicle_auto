import logging
from logging.handlers import RotatingFileHandler
import os

class CCLogger(object):

    __logger = None

    def __init__(self, tail_name='default'):
        if CCLogger.__logger:
            raise CCLogger.__logger
        file_formatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
                                           '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        console_formatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
                                              '(%(lineno)d) - %(message)s', datefmt='%B %d %H:%M:%S')

        # consoleFormatter = logging.Formatter('%(asctime)s: [%(levelname)s]' \
        # ' - %(message)s', datefmt='%B %d %H:%M:%S')

        log_basepath = 'logs'
        if not os.path.exists(log_basepath):
            os.makedirs(log_basepath)

        CCLogger.__logger = logging.getLogger("Chain Chronicle")
        CCLogger.__logger.setLevel(logging.DEBUG)
        log_name = "cc_{0}.log".format(tail_name)
        log_path = os.path.join(log_basepath, log_name)
        rh = RotatingFileHandler(log_path, maxBytes=1024 * 10000, backupCount=5)
        rh.setLevel(logging.DEBUG)
        rh.setFormatter(file_formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(console_formatter)

        CCLogger.__logger.addHandler(rh)
        CCLogger.__logger.addHandler(console)

    @staticmethod
    def get_logger(log_id):
        if CCLogger.__logger is None:
            CCLogger(log_id)
        return CCLogger.__logger



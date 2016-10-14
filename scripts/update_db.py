# -*- coding: utf-8 -*
import argparse
import sys
sys.path.append('../')
import utils.db_operator


def main():
    utils.db_operator.DBUpdater.update_db()

if __name__ == '__main__':
    main()

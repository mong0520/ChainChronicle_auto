# -*- coding: utf-8 -*
import argparse
import sys
sys.path.append('../')
import utils.db_operator


def query(args):
    utils.db_operator.DBOperator.dump_quest(args.quest)


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-n', '--quest', help='quest name to match', required=True, action='store')
    args = parser.parse_args()
    query(args)

if __name__ == '__main__':
    main()

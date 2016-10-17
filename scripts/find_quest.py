# -*- coding: utf-8 -*
import argparse
import sys
sys.path.append('../')


def query(args):
    import utils.db_operator
    utils.db_operator.DBOperator.dump_quest(args.quest, args.verbose)


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-n', '--quest', help='quest name to match', required=True, action='store')
    parser.add_argument('-v', '--verbose', help='quest name to match', required=False, action='store_true')
    args = parser.parse_args()
    query(args)

if __name__ == '__main__':
    main()

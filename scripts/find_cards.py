# -*- coding: utf-8 -*
import argparse
import sys
sys.path.append('../')
import utils.db_operator


def query(args):
    utils.db_operator.DBOperator.dump_cards(args.field, args.value)
    # utils.db_operator.DBOperator.dump_cards('title', '狐尾')


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-f', '--field', help='field to query', required=True, action='store')
    parser.add_argument('-v', '--value', help='field value to match', required=True, action='store')
    args = parser.parse_args()
    query(args)

if __name__ == '__main__':
    main()

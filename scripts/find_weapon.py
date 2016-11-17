# -*- coding: utf-8 -*
import argparse
import sys
sys.path.append('../')


def query(args):
    import utils.db_operator
    utils.db_operator.DBOperator.dump_weapon(args.field, args.value)


def main():
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-f', '--field', help='field to query', required=True, action='store')
    parser.add_argument('-v', '--value', help='field value to match', required=True, action='store')
    args = parser.parse_args()
    query(args)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils.db_operator


def query(args):
    utils.db_operator.DBOperator.dump_general(args.source, args.field, args.value)


def main():
    valid_source = utils.db_operator.data_mapping.keys()
    parser = argparse.ArgumentParser(description="Chain Chronicle Query tool")
    parser.add_argument('-s', '--source', help='db source file', required=True, action='store', choices=valid_source)
    parser.add_argument('-f', '--field', help='field name', required=False, action='store')
    parser.add_argument('-v', '--value', help='field value', required=False, action='store')
    args = parser.parse_args()
    query(args)

if __name__ == '__main__':
    main()
    # python find_general.py -s charainfo -f name -v 曉

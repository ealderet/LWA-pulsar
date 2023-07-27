#!/usr/bin/env python3

import os
import re
import tempfile
import argparse


def main(args):
    filename = args.filename

    with open(filename) as file:
        lines = [next(file) for x in range(26)]
        file.close()

    DM = float(lines[14].split()[-1])
    
    SNR = float(lines[13].split()[-2].strip('(~'))

    PER_TOPO = float(lines[15].split()[-3])
    PER_TOPO_ERR = float(lines[15].split()[-1])
    PER_BARY = float(lines[18].split()[-3])
    PER_BARY_ERR = float(lines[18].split()[-1])

    print(DM)
    print(SNR)
    print(PER_TOPO)
    print(PER_BARY)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='currently only grabs DM of prepfold pulsar fold',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument('filename', type=str, 
                        help='filename of _______.bestprof file')
    args = parser.parse_args()
    main(args)

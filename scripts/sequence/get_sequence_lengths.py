#!/usr/bin/env python
__author__ = 'mahajrod'

import argparse
import os

from Bio import SeqIO

from Routines.Sequence import get_lengths

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--format", action="store", dest="format",
                    default="fasta", help="format of file with sequences - default: fasta.")
parser.add_argument("-i", "--input", action="store", dest="input",
                    help="file with sequences")
parser.add_argument("-o", "--output", action="store", dest="output",
                    default="out.t", help="output file - default: out.t.")
parser.add_argument("-w", "--write_header", action="store_true", dest="write_header",
                    default=False, help="Write header. Default: False")
args = parser.parse_args()

record_dict = SeqIO.index_db("temp_index.idx", [args.input], format=args.format)
get_lengths(record_dict, out_file=args.output, write=True, write_header=args.write_header)

os.remove("temp_index.idx")
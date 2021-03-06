__author__ = 'mahajrod'
import os
import re
import sys
import pickle

from copy import deepcopy
from collections import OrderedDict

import numpy as np

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

from CustomCollections.GeneralCollections import TwoLvlDict, SynDict, IdList, IdSet
from Routines.Functions import output_dict
from Routines.File import FileRoutines


class FastQRoutines(FileRoutines):

    def __init__(self):
        pass

    @staticmethod
    def reverse_complement(in_file, out_file):
        with open(in_file, "r") as in_fd:
            with open(out_file, "w") as out_fd:
                for line in in_fd:
                    out_fd.write(line)
                    out_fd.write(str(Seq(in_fd.next().strip()).reverse_complement()))
                    out_fd.write("\n")
                    out_fd.write(in_fd.next())
                    out_fd.write(in_fd.next().strip()[::-1])
                    out_fd.write("\n")

    @staticmethod
    def parse_illumina_name(string):
        name_list = string[1:].split(" ")

    def remove_tiles_from_fastq(self, forward_reads, black_list_forward_tiles_list,
                                reverse_reads, black_list_reverse_tiles_list, output_prefix):

        filtered_paired_forward_pe = "%s.ok.pe_1.fastq" % output_prefix
        filtered_forward_se = "%s.ok.forward.se.fastq" % output_prefix
        filtered_out_forward_se = "%s.bad.forward.fastq" % output_prefix

        filtered_paired_reverse_pe = "%s.ok.pe_2.fastq" % output_prefix
        filtered_reverse_se = "%s.ok.reverse.se.fastq" % output_prefix
        filtered_out_reverse_se = "%s.bad.reverse.fastq" % output_prefix

        forward_input_fd = self.metaopen(forward_reads, "r")
        reverse_input_fd = self.metaopen(reverse_reads, "r")

        filtered_paired_forward_pe_fd = self.metaopen(filtered_paired_forward_pe, "w")
        filtered_forward_se_fd = self.metaopen(filtered_forward_se, "w")
        filtered_out_forward_se_fd = self.metaopen(filtered_out_forward_se, "w")

        filtered_paired_reverse_pe_fd = self.metaopen(filtered_paired_reverse_pe, "w")
        filtered_reverse_se_fd = self.metaopen(filtered_reverse_se, "w")
        filtered_out_reverse_se_fd = self.metaopen(filtered_out_reverse_se, "w")

        for line in forward_input_fd:
            name_list = line.strip()[1:].split(":")
            #instrument_id = name_list[0]
            #run_id = name_list[1]
            #flowcell_id = name_list[2]
            #lane_id = name_list[3]
            tile_id = name_list[4]

            if (tile_id in black_list_forward_tiles_list) and (tile_id in black_list_reverse_tiles_list):
                filtered_out_forward_se_fd.write(line)
                for i in range(0, 3):
                    filtered_out_forward_se_fd.write(forward_input_fd.next())
                for i in range(0, 4):
                    filtered_out_reverse_se_fd.write(reverse_input_fd.next())

            elif (tile_id in black_list_forward_tiles_list) and (not(tile_id in black_list_reverse_tiles_list)):
                filtered_out_forward_se_fd.write(line)
                for i in range(0, 3):
                    filtered_out_forward_se_fd.write(forward_input_fd.next())
                for i in range(0, 4):
                    filtered_reverse_se_fd.write(reverse_input_fd.next())

            elif (not (tile_id in black_list_forward_tiles_list)) and (tile_id in black_list_reverse_tiles_list):
                filtered_forward_se_fd.write(line)
                for i in range(0, 3):
                    filtered_forward_se_fd.write(forward_input_fd.next())
                for i in range(0, 4):
                    filtered_out_reverse_se_fd.write(reverse_input_fd.next())

            else:
                filtered_paired_forward_pe_fd.write(line)
                for i in range(0, 3):
                    filtered_paired_forward_pe_fd.write(forward_input_fd.next())
                for i in range(0, 4):
                    filtered_paired_reverse_pe_fd.write(reverse_input_fd.next())

        filtered_paired_forward_pe_fd.close()
        filtered_forward_se_fd.close()
        filtered_out_forward_se_fd.close()

        filtered_paired_reverse_pe_fd.close()
        filtered_reverse_se_fd.close()
        filtered_out_reverse_se_fd.close()

    def combine_fastq_files(self, samples_directory, sample, output_directory,
                            use_links_if_merge_not_necessary=True):
        sample_dir = "%s/%s/" % (samples_directory, sample)
        filetypes, forward_files, reverse_files = self.make_lists_forward_and_reverse_files(sample_dir)
        if len(filetypes) == 1:
            if ("fq.gz" in filetypes) or ("fastq.gz" in filetypes):
                command = "zcat"
            elif ("fq.bz2" in filetypes) or ("fastq.bz2" in filetypes):
                command = "bzcat"
            else:
                command = "cat"

            if use_links_if_merge_not_necessary and (len(forward_files) == 1) and (len(reverse_files) == 1):
                os.system("ln -s %s %s/%s_1.fq" % (forward_files[0], output_directory, sample))
                os.system("ln -s %s %s/%s_2.fq" % (reverse_files[0], output_directory, sample))
            else:
                os.system("%s %s > %s/%s_1.fq" % (command, " ".join(forward_files), output_directory, sample))
                os.system("%s %s > %s/%s_2.fq" % (command, " ".join(reverse_files), output_directory, sample))
        else:
            raise IOError("Extracting from mix of archives in not implemented yet")

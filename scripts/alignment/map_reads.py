#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'
import os
import sys
import argparse

from numpy import mean, median, array

from Tools.Alignment import *
from Tools.Samtools import SamtoolsV1, SamtoolsV0
from Tools.Picard import AddOrReplaceReadGroups
from Tools.Bedtools import GenomeCov

from CustomCollections.GeneralCollections import SynDict


def make_list_from_comma_sep_string(s):
    return s.split(",")

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--aligner_index", action="store", dest="index",
                    help="Aligner-specific index")
parser.add_argument("-a", "--aligner", action="store", dest="aligner", default="bowtie2",
                    help="Aligner to use. Possible aligners: bowtie2. Default: bowtie2")
parser.add_argument("-t", "--threads", action="store", dest="threads", default=4, type=int,
                    help="Number of threads. Default: 4")
parser.add_argument("-b", "--bed_with_regions", action="store", dest="bed",
                    help="Bed file with regions to output.")
parser.add_argument("-r", "--right_reads", action="store", dest="right_reads",
                    type=make_list_from_comma_sep_string,
                    help="Comma-separated list of files with right reads")
parser.add_argument("-l", "--left_reads", action="store", dest="left_reads",
                    type=make_list_from_comma_sep_string,
                    help="Comma-separated list of files with left reads")
parser.add_argument("-u", "--unpaired_reads", action="store", dest="unpaired_reads",
                    type=make_list_from_comma_sep_string,
                    help="Comma-separated list of files with unpaired reads")
parser.add_argument("-q", "--quality", action="store", dest="quality", default="phred33",
                    help="Quality type. Possible variants phred33, phred64. Default: phred33")
parser.add_argument("-p", "--prefix", action="store", dest="prefix", default="alignment",
                    help="Prefix of output files")
parser.add_argument("-c", "--black_flag_value", action="store", dest="black_flag_value", type=int,
                    help="Black bam flag value. By default unaligned, supplementary alignments and "
                         "nonprimary alignments will be removed")
parser.add_argument("-e", "--white_flag_value", action="store", dest="white_flag_value", type=int,
                    help="White flag value")
parser.add_argument("-g", "--dont_add_read_groups", action="store_true", dest="dont_add_read_groups", default=False,
                    help="Don't add read groups to final bam")
parser.add_argument("-d", "--picard_dir", action="store", dest="picard_dir",
                    help="Path to Picard directory. Required to add read groups")
parser.add_argument("-n", "--retain_intermediate_files", action="store_true", dest="retain_temp", default=False,
                    help="Retain intermediate files")
parser.add_argument("-y", "--coverage_bed", action="store", dest="coverage_bed", default="coverage.bed",
                    help="Bed file with coverage")
parser.add_argument("-z", "--calculate_median_coverage", action="store_true", dest="calculate_median_coverage",
                    default=False,
                    help="Calculate median coverage")
parser.add_argument("-x", "--calculate_mean_coverage", action="store_true", dest="calculate_mean_coverage",
                    default=False,
                    help="Calculate mean coverage")
parser.add_argument("-f", "--flanks_size", action="store", dest="flanks_size",
                    default=0, type=int,
                    help="Size of flanks to remove when calculating mean/median coverage")
args = parser.parse_args()

black_flag_value = args.black_flag_value if args.black_flag_value else \
    SamtoolsV0.bam_flag_values["unaligned"] + SamtoolsV0.bam_flag_values["supplementary_alignment"] \
    + SamtoolsV0.bam_flag_values["non_primary_alignment"]

raw_alignment = "%s_raw_alignment.sam" % args.prefix
filtered_alignment = "%s_filtered.bam" % args.prefix
sorted_filtered_alignment_prefix = "%s_filtered_sorted" % args.prefix
sorted_filtered_alignment = "%s_filtered_sorted.bam" % args.prefix
rmdup_sorted_filtered_alignment = "%s_final.bam" % args.prefix
rmdup_sorted_filtered_alignment_with_groups = "%s_final_with_groups.bam" % args.prefix
if args.aligner == "bowtie2":
    aligner = Bowtie2

aligner.threads = args.threads


aligner.align(args.index, right_reads_list=args.right_reads, left_reads_list=args.left_reads,
              unpaired_reads_list=args.unpaired_reads, quality_score=args.quality, output_file=raw_alignment)


"""
# Samtools version 1+.  Rmdup doesnt work with bams containing reads from several libraries
SamtoolsV1.threads = args.threads
SamtoolsV1.view(raw_alignment, output_file=filtered_alignment, include_header_in_output=True,
              output_uncompressed_bam=True, output_bam=True, white_flag_value=args.white_flag_value,
              black_flag_value=black_flag_value, bed_file_with_regions_to_output=args.bed)
SamtoolsV1.sort(filtered_alignment, sorted_filtered_alignment, temp_file_prefix="temp_bam")
SamtoolsV1.rmdup(sorted_filtered_alignment, rmdup_sorted_filtered_alignment, treat_both_pe_and_se_reads=False)
"""

# Samtools v 0.1.19

SamtoolsV0.view(raw_alignment, output_file=filtered_alignment, include_header_in_output=True,
                output_uncompressed_bam=True, output_bam=True, white_flag_value=args.white_flag_value,
                black_flag_value=black_flag_value, bed_file_with_regions_to_output=args.bed,
                sam_input=True)
SamtoolsV0.sort(filtered_alignment, sorted_filtered_alignment_prefix)


SamtoolsV0.rmdup(sorted_filtered_alignment, rmdup_sorted_filtered_alignment, treat_both_pe_and_se_reads=False)

if not args.dont_add_read_groups:
    AddOrReplaceReadGroups.jar_path = args.picard_dir
    AddOrReplaceReadGroups.add_read_groups(rmdup_sorted_filtered_alignment, rmdup_sorted_filtered_alignment_with_groups,
                                           RGID=args.prefix, RGLB=args.prefix, RGPL=args.prefix,
                                           RGSM=args.prefix, RGPU=args.prefix)
    #os.remove(rmdup_sorted_filtered_alignment)
    #os.rename("temp.bam", rmdup_sorted_filtered_alignment)

SamtoolsV0.index(rmdup_sorted_filtered_alignment_with_groups if not args.dont_add_read_groups else rmdup_sorted_filtered_alignment)
GenomeCov.get_coverage(rmdup_sorted_filtered_alignment_with_groups if not args.dont_add_read_groups else rmdup_sorted_filtered_alignment, args.coverage_bed)
if not args.retain_temp:
    os.remove(raw_alignment)
    os.remove(filtered_alignment)
    os.remove(sorted_filtered_alignment)

if args.calculate_median_coverage or args.calculate_mean_coverage:
    coverage_dict = SynDict()
    coverage_dict.read(args.coverage_bed, header=False, separator="\t", allow_repeats_of_key=True,
                       values_separator=",", key_index=0, value_index=2, expression=int)
    if args.calculate_median_coverage:
        with open("%s_median_coverage.tab" % args.prefix, "w") as out_fd:
            for region in coverage_dict:
                mediana = median(array(coverage_dict[region] if args.flanks_size == 0
                                       else coverage_dict[region][args.flanks_size:-args.flanks_size]))
                out_fd.write("%s\t%f\n" % (region, mediana))
    if args.calculate_mean_coverage:
        with open("%s_mean_coverage.tab" % args.prefix, "w") as out_fd:
            for region in coverage_dict:
                meana = mean(array(coverage_dict[region] if args.flanks_size == 0
                                   else coverage_dict[region][args.flanks_size:-args.flanks_size]))
                out_fd.write("%s\t%f\n" % (region, meana))

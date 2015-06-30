#!/usr/bin/env python
__author__ = 'mahajrod'
import os
import argparse
from random import choice

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import linspace

from collections import OrderedDict
from CustomCollections.GeneralCollections import TwoLvlDict
from Parsers.CAFE import ReportCAFE


parser = argparse.ArgumentParser()

parser.add_argument("-c", "--cafe_report", action="store", dest="cafe_report",
                    help="Input cafe report")
parser.add_argument("-n", "--convert", action="store_true", dest="convert_flag", default=False,
                    help="If present enables conversion of report to tree and node variants")
parser.add_argument("-g", "--general_trees_prefix", action="store", dest="general_trees_prefix", default="general_tree",
                    help="Prefix for general trees")
parser.add_argument("-o", "--output_prefix", action="store", dest="out_prefix", default="node",
                    help="Prefix for node specific output")
parser.add_argument("-f", "--family_pvalue", action="store", dest="family_p_value", type=float, default=0.05,
                    help="Family p-value cutoff")
parser.add_argument("-p", "--node_pvalue", action="store", dest="node_p_value", type=float, default=0.05,
                    help="Node p-value cutoff")
parser.add_argument("-r", "--ref_species_gene_file", action="store", dest="ref_species_gene_file",
                    help="File with gene of genes families of reference species ")
args = parser.parse_args()

general_trees_dir = "general_trees/"
node_info_dir = "node_info/"
node_ref_dir = "node_ref/"
converted_dir = "converted/"
statistics_dir = "statistics/"
background_genes_dir = "background/"
hist_subdir = "histogram/"

for directory in general_trees_dir, node_info_dir, node_ref_dir, converted_dir, statistics_dir, background_genes_dir:
    try:
        os.mkdir(directory)
    except OSError:             # intercept exception raised if directory already exists
        pass
for directory in node_info_dir, node_ref_dir:
    for subdirectory in "all/", "new/", "lost/":
        try:
            os.mkdir(directory + subdirectory)
        except OSError:             # intercept exception raised if directory already exists
            pass
try:
    os.mkdir(node_info_dir + hist_subdir)
except OSError:             # intercept exception raised if directory already exists
    pass
cafe_report = ReportCAFE(report_file=args.cafe_report, from_file=True)
if args.convert_flag:
    for output_type in "tree", "node":
        print("Converting report to %s format" % output_type)
        cafe_report.convert(converted_dir + "converted_report_mode_%s.t" % output_type, output_type=output_type)
cafe_report.general_data.draw(general_trees_dir + args.general_trees_prefix)

filtered_report, filtered_out_report = cafe_report.filter_by_family_p_value(args.family_p_value)
node_values, features_list = filtered_report.get_per_node_values(filter_by_p_value=True,
                                                                 p_value_cutoff=args.node_p_value)
print("Totally %i gene families without statistically significant changes" % len(filtered_out_report.records))

reference_genes_dict = {}
with open(args.ref_species_gene_file, "r") as ref_fd:
    for line in ref_fd:
        gene_family_id, genes = line.strip().split("\t")
        genes = [] if genes == "." else genes.split(",")
        reference_genes_dict[gene_family_id] = [genes[:]]
        if genes:
            reference_genes_dict[gene_family_id].append(choice(genes))

node_header_list = features_list + ["reference_gene"]
delta_index = features_list.index("delta")
statistics_dict = TwoLvlDict({})

for node_id in node_values:
    statistics_dict[node_id] = OrderedDict({"lost": 0, "new": 0, "lost_ref_ann": 0, "new_ref_ann": 0})

for node_id in node_values:
    fd_list = []
    for directory in node_info_dir, node_ref_dir:
        for mode in "all", "new", "lost":
            fd_list.append(open(directory + "%s/%s_%s_%s.t" % (mode, args.out_prefix, node_id, mode), "w"))

    all_fd, new_fd, lost_fd, all_ref_id_fd, new_ref_id_fd, lost_ref_id_fd = fd_list

    for fd in all_fd, new_fd, lost_fd:
        fd.write("#%s\n" % "\t".join(node_header_list))
    lost_values = []
    new_values = []
    for entry in node_values[node_id]:
        if entry[delta_index] is None:
            continue
        node_string = "\t".join(map(lambda x: str(x), entry))
        node_reference_genes = reference_genes_dict[entry[0]][0]
        if node_reference_genes:
            random_reference_gene = reference_genes_dict[entry[0]][1]
            all_ref_id_fd.write(random_reference_gene + "\n")
        else:
            random_reference_gene = "."
        node_string += "\t%s\n" % random_reference_gene
        all_fd.write(node_string)
        if entry[delta_index] > 0:
            new_fd.write(node_string)
            statistics_dict[node_id]["new"] += 1
            new_values.append(entry[delta_index])
            if node_reference_genes:
                new_ref_id_fd.write(random_reference_gene + "\n")
                statistics_dict[node_id]["new_ref_ann"] += 1
        elif entry[delta_index] < 0:
            lost_fd.write(node_string)
            statistics_dict[node_id]["lost"] += 1
            lost_values.append(-entry[delta_index])
            if node_reference_genes:
                lost_ref_id_fd.write(random_reference_gene + "\n")
                statistics_dict[node_id]["lost_ref_ann"] += 1

    plt.figure(1, figsize=(5, 10))
    index = 1
    subplot_list = []
    for values, info in zip([new_values, lost_values], ["new", "lost"]):
        if not values:
            continue
        maximum = max(values)
        subplot_list.append(plt.subplot(2, 1, index))
        bins = linspace(1, maximum, maximum)
        plt.hist(values, bins=bins)
        plt.xlabel("Number of %s genes in family" % info)
        plt.xlim(xmin=1)
        plt.ylabel("Number of families")
        index += 1
    plt.suptitle("Distribution of losses and additions in gene families")
    plt.savefig(node_info_dir + hist_subdir + "%s_%s.svg" % (args.out_prefix, node_id))
    plt.close()
    for fd in fd_list:
        fd.close()

with open(background_genes_dir + "background_genes.t", "w") as back_fd:
    with open(background_genes_dir + "background_genes_list.txt", "w") as back_list_fd:
        back_fd.write("#id\tfamaliy_p_value\tref_gene\n")
        for record in filtered_out_report:
            #print(record)
            if reference_genes_dict[record.id][0]:
                random_reference_gene = choice(reference_genes_dict[record.id][0])
                back_list_fd.write(random_reference_gene + "\n")
            else:
                random_reference_gene = "."
            back_string = "%s\t%f\t%s\n" % (record.id, record.family_p_value, random_reference_gene)
            back_fd.write(back_string)

statistics_dict.write(statistics_dir + "node_statistics.t", absent_symbol=".")



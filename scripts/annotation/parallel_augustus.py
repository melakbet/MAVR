#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'
import os
import shutil
import argparse

from Tools.HMMER import HMMER3
from Tools.BLAST import BLASTp
from Tools.Bedtools import Intersect
from Tools.Annotation import AUGUSTUS

from Routines import AnnotationsRoutines, MatplotlibRoutines, SequenceRoutines

from CustomCollections.GeneralCollections import IdSet

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", action="store", dest="input", required=True,
                    help="Input fasta file with sequences")
parser.add_argument("-o", "--output", action="store", dest="output", required=True,
                    help="Prefix of output files")
parser.add_argument("-t", "--threads", action="store", dest="threads", type=int, default=1,
                    help="Number of threads to use")

parser.add_argument("-s", "--species", action="store", dest="species", required=True,
                    help="Species to use as model")
parser.add_argument("-r", "--strand", action="store", dest="strand", default="both",
                    help="Strand to consider. Possible variants: both, forward, backward."
                         "Default: both")
parser.add_argument("-g", "--gene_model", action="store", dest="gene_model",
                    help="Gene model to use. Possible variants:"
                         "partial      : allow prediction of incomplete genes at the sequence boundaries (default)"
                         "intronless   : only predict single-exon genes like in prokaryotes and some eukaryotes"
                         "complete     : only predict complete genes"
                         "atleastone   : predict at least one complete gene"
                         "exactlyone   : predict exactly one complete gene"
                         "Default: complete")
parser.add_argument("-e", "--other_options", action="store", dest="other_options",
                    help="Other augustus options")
parser.add_argument("-c", "--augustus_config_dir", action="store", dest="config_dir",
                    help="Augustus config dir")
parser.add_argument("-p", "--pfam_hmm3", action="store", dest="pfam_db",
                    help="Pfam database in hmm3 format")
parser.add_argument("-w", "--swissprot_blast_db", action="store", dest="swissprot_db",
                    help="Blast database of swissprot")
parser.add_argument("-m", "--masking", action="store", dest="masking",
                    help="Gff of bed file with masking of repeats")
parser.add_argument("--softmasking", action="store_true", dest="softmasking",
                    help="Use softmasking from genome")
parser.add_argument("--hintsfile", action="store", dest="hintsfile",
                    help="File with hints")
parser.add_argument("--extrinsicCfgFile", action="store", dest="extrinsicCfgFile",
                    help="Config file with scoring for hints")
parser.add_argument("-u", "--predict_UTR", action="store_true", dest="predict_UTR",
                    help="Predict UTR. works not for all species")
parser.add_argument("-a", "--augustus_dir", action="store", dest="augustus_dir", default="",
                    help="Directory with augustus binary")

args = parser.parse_args()

output_gff = "%s.gff" % args.output
output_pep = "%s.pep" % args.output
output_evidence_stats = "%s.transcript.evidence" % args.output
output_evidence_stats_longest_pep = "%s.transcript.evidence.longest_pep" % args.output
output_supported_stats = "%s.transcript.supported" % args.output
output_supported_stats_ids = "%s.transcript.supported.ids" % args.output
output_supported_stats_longest_pep = "%s.transcript.supported.longest_pep" % args.output
output_hmmscan = "%s.hmmscan.hits" % args.output
output_domtblout = "%s.domtblout" % args.output
output_pfam_annotated_dom_ids = "%s.pfam.dom_ids" % args.output
#output_pfam_supported_ids = "%s.supported.pfam.ids" % args.output
output_pfam_supported_transcripts_ids = "%s.supported.transcripts.pfam.ids" % args.output
output_pfam_supported_genes_ids = "%s.supported.genes.pfam.ids" % args.output

output_pfam_annotated_dom_names = "%s.pfam.dom_names" % args.output

output_swissprot_blastp_hits = "%s.swissprot.hits" % args.output
#output_swissprot_supported_ids = "%s.supported.swissprot.ids" % args.output
output_swissprot_supported_transcripts_ids = "%s.supported.transcripts.swissprot.ids" % args.output
output_swissprot_supported_genes_ids = "%s.supported.genes.swissprot.ids" % args.output
output_swissprot_blastp_hits_names = "%s.swissprot.hits.names" % args.output

output_swissprot_pfam_supported_transcripts_ids = "%s.supported.transcripts.swissprot_or_pfam.ids" % args.output
output_swissprot_pfam_or_hints_supported_transcripts_ids = "%s.supported.transcripts.swissprot_or_pfam_or_hints.ids" % args.output
output_swissprot_pfam_and_hints_supported_transcripts_ids = "%s.supported.transcripts.swissprot_or_pfam_and_hints.ids" % args.output
output_swissprot_pfam_or_hints_supported_transcripts_evidence = "%s.supported.transcripts.swissprot_or_pfam_or_hints.evidence" % args.output
output_swissprot_pfam_and_hints_supported_transcripts_evidence = "%s.supported.transcripts.swissprot_or_pfam_and_hints.evidence" % args.output
output_swissprot_pfam_or_hints_supported_transcripts_pep = "%s.supported.transcripts.swissprot_or_pfam_or_hints.pep" % args.output
output_swissprot_pfam_and_hints_supported_transcripts_pep = "%s.supported.transcripts.swissprot_or_pfam_and_hints.pep" % args.output

output_swissprot_pfam_or_hints_supported_transcripts_longest_pep_evidence = "%s.supported.transcripts.swissprot_or_pfam_or_hints.longest_pep.evidence" % args.output
output_swissprot_pfam_and_hints_supported_transcripts_longest_pep_evidence = "%s.supported.transcripts.swissprot_or_pfam_and_hints.longest_pep.evidence" % args.output
output_swissprot_pfam_or_hints_supported_transcripts_longest_pep = "%s.supported.transcripts.swissprot_or_pfam_or_hints.longest_pep.pep" % args.output
output_swissprot_pfam_and_hints_supported_transcripts_longest_pep = "%s.supported.transcripts.swissprot_or_pfam_and_hints.longest_pep.pep" % args.output


CDS_gff = "%s.CDS.gff" % args.output
CDS_masked_gff = "%s.CDS.masked.gff" % args.output
all_annotated_genes_ids = "%s.genes.all.ids" % args.output
genes_masked_ids = "%s.genes.masked.ids" % args.output
genes_not_masked_ids = "%s.genes.not.masked.ids" % args.output
final_genes_ids = "%s.genes.final.ids" % args.output

final_gff = "%s.final.gff" % args.output
final_CDS_gff = "%s.final.CDS.gff" % args.output

AUGUSTUS.path = args.augustus_dir
AUGUSTUS.threads = args.threads

print("Annotating genes...")

AUGUSTUS.parallel_predict(args.species, args.input, output_gff, strand=args.strand, gene_model=args.gene_model,
                          output_gff3=True, other_options=args.other_options, config_dir=args.config_dir,
                          use_softmasking=args.softmasking, hints_file=args.hintsfile,
                          extrinsicCfgFile=args.extrinsicCfgFile, predict_UTR=args.predict_UTR)


AUGUSTUS.extract_gene_ids_from_output(output_gff, all_annotated_genes_ids)
AUGUSTUS.extract_CDS_annotations_from_output(output_gff, CDS_gff)
if args.masking:
    print("Intersecting annotations with repeats...")
    Intersect.intersect(CDS_gff, args.masking, CDS_masked_gff, method="-u")
    sed_string = "sed 's/.*=//;s/\.t.*//' %s | sort | uniq > %s" % (CDS_masked_gff, genes_masked_ids)
    os.system(sed_string)

print("Extracting peptides...")

AUGUSTUS.extract_proteins_from_output(output_gff, output_pep, id_prefix="", evidence_stats_file=output_evidence_stats,
                                      supported_by_hints_file=output_supported_stats)

os.system("awk -F'\\t' 'NR==1 {}; NR > 1 {print $2}' %s > %s" % (output_supported_stats, output_supported_stats_ids))

if args.pfam_db:
    print("Annotating domains(Pfam database)...")
    HMMER3.threads = args.threads
    HMMER3.parallel_hmmscan(args.pfam_db, output_pep, output_hmmscan, num_of_seqs_per_scan=None, split_dir="splited_hmmscan_fasta/",
                            splited_output_dir="splited_hmmscan_output_dir",
                            tblout_outfile=None, domtblout_outfile=output_domtblout, pfamtblout_outfile=None,
                            splited_tblout_dir=None, splited_domtblout_dir="hmmscan_domtblout/")
    HMMER3.extract_dom_ids_hits_from_domtblout(output_domtblout, output_pfam_annotated_dom_ids)
    hits_dict = HMMER3.extract_dom_names_hits_from_domtblout(output_domtblout, output_pfam_annotated_dom_names)
    supported_ids = IdSet(hits_dict.keys())
    supported_ids.write(output_pfam_supported_transcripts_ids)
    remove_transcript_ids_str = "sed -re 's/\.t[0123456789]+//' %s | sort -k 1 | uniq > %s" % (output_pfam_supported_transcripts_ids,
                                                                                               output_pfam_supported_genes_ids)
    os.system(remove_transcript_ids_str)

    for directory in ("splited_hmmscan_fasta/", "splited_hmmscan_output_dir", "hmmscan_domtblout/"):
        shutil.rmtree(directory)

if args.swissprot_db:
    print("Annotating peptides(Swissprot database)...")
    BLASTp.threads = args.threads
    BLASTp.parallel_blastp(output_pep, args.swissprot_db, evalue=0.0000001, output_format=6,
                           outfile=output_swissprot_blastp_hits, split_dir="splited_blastp_fasta",
                           splited_output_dir="splited_blastp_output_dir")
    hits_dict = BLASTp.extract_hits_from_tbl_output(output_swissprot_blastp_hits, output_swissprot_blastp_hits_names)
    supported_ids = IdSet(hits_dict.keys())
    supported_ids.write(output_swissprot_supported_transcripts_ids)

    remove_transcript_ids_str = "sed -re 's/\.t[0123456789]+//' %s | sort -k 1 | uniq > %s" % (output_swissprot_supported_transcripts_ids,
                                                                                               output_swissprot_supported_genes_ids)
    os.system(remove_transcript_ids_str)

    for directory in ("splited_blastp_fasta", "splited_blastp_output_dir"):
        shutil.rmtree(directory)

gene_ids_black_list = [genes_masked_ids] if args.masking else []
gene_ids_white_list = []
if args.pfam_db and args.swissprot_db:
    gene_ids_white_list = [output_pfam_supported_genes_ids, output_swissprot_supported_genes_ids]
    HMMER3.intersect_ids_from_files(output_swissprot_supported_transcripts_ids, output_pfam_supported_transcripts_ids,
                                    output_swissprot_pfam_supported_transcripts_ids, mode="combine")
    HMMER3.intersect_ids_from_files(output_swissprot_pfam_supported_transcripts_ids, output_supported_stats_ids,
                                    output_swissprot_pfam_or_hints_supported_transcripts_ids, mode="combine")
    HMMER3.intersect_ids_from_files(output_swissprot_pfam_supported_transcripts_ids, output_supported_stats_ids,
                                    output_swissprot_pfam_and_hints_supported_transcripts_ids, mode="common")

    SequenceRoutines.extract_sequence_by_ids(output_pep, output_swissprot_pfam_or_hints_supported_transcripts_ids,
                                             output_swissprot_pfam_or_hints_supported_transcripts_pep)
    SequenceRoutines.extract_sequence_by_ids(output_pep, output_swissprot_pfam_and_hints_supported_transcripts_ids,
                                             output_swissprot_pfam_and_hints_supported_transcripts_pep)

    AUGUSTUS.extract_evidence_by_ids(output_evidence_stats, output_swissprot_pfam_or_hints_supported_transcripts_ids,
                                     output_swissprot_pfam_or_hints_supported_transcripts_evidence)
    AUGUSTUS.extract_evidence_by_ids(output_evidence_stats, output_swissprot_pfam_and_hints_supported_transcripts_ids,
                                     output_swissprot_pfam_and_hints_supported_transcripts_evidence)
    AUGUSTUS.extract_longest_isoforms(output_swissprot_pfam_or_hints_supported_transcripts_evidence,
                                      output_swissprot_pfam_or_hints_supported_transcripts_longest_pep_evidence)
    AUGUSTUS.extract_longest_isoforms(output_swissprot_pfam_and_hints_supported_transcripts_evidence,
                                      output_swissprot_pfam_and_hints_supported_transcripts_longest_pep_evidence)

    SequenceRoutines.extract_sequence_by_ids(output_pep, "%s.ids" % output_swissprot_pfam_or_hints_supported_transcripts_longest_pep_evidence,
                                             output_swissprot_pfam_or_hints_supported_transcripts_longest_pep)
    SequenceRoutines.extract_sequence_by_ids(output_pep, "%s.ids" % output_swissprot_pfam_and_hints_supported_transcripts_longest_pep_evidence,
                                             output_swissprot_pfam_and_hints_supported_transcripts_longest_pep)

elif args.pfam_db:
    gene_ids_white_list = [output_pfam_supported_genes_ids]
elif args.swissprot_db:
    gene_ids_white_list = [output_swissprot_supported_genes_ids]
else:
    gene_ids_white_list = [all_annotated_genes_ids]

HMMER3.intersect_ids_from_files([all_annotated_genes_ids], gene_ids_black_list, genes_not_masked_ids, mode="only_a")
HMMER3.intersect_ids_from_files(gene_ids_white_list, gene_ids_black_list, final_genes_ids, mode="only_a")

final_ids = IdSet()
final_ids.read(final_genes_ids)

AnnotationsRoutines.extract_annotation_from_gff(output_gff, final_ids, ["gene"], final_gff)
AUGUSTUS.extract_CDS_annotations_from_output(final_gff, final_CDS_gff)


for stat_file in output_evidence_stats, output_supported_stats, \
                 output_swissprot_pfam_or_hints_supported_transcripts_longest_pep_evidence, \
                 output_swissprot_pfam_and_hints_supported_transcripts_longest_pep_evidence, \
                 output_swissprot_pfam_or_hints_supported_transcripts_evidence, output_swissprot_pfam_and_hints_supported_transcripts_evidence:

    MatplotlibRoutines.percent_histogram_from_file(stat_file, stat_file, data_type=None,
                                                   column_list=(2,),
                                                   comments="#", n_bins=20,
                                                   title="Transcript support by hints",
                                                   extensions=("png", "svg"),
                                                   legend_location="upper center",
                                                   stats_as_legend=True)

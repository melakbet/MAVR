#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'
import shutil
import argparse

from Tools.HMMER import HMMER3
from Tools.BLAST import BLASTp
from Tools.Annotation import AUGUSTUS

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
parser.add_argument("-g", "--gene_model", action="store", dest="gene_model", default="complete",
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
parser.add_argument("-s", "--swissprot_blast_db", action="store", dest="swissprot_db",
                    help="Blast database of swissprot")

args = parser.parse_args()

output_pep = "%s.pep" % args.output
output_domtblout = "%s.domtblout" % args.output
output_pfam_annotated_dom_ids = "%s.pfam.dom_ids" % args.output
output_pfam_annotated_dom_names = "%s.pfam.dom_names" % args.output
output_swissprot_blastp_hits = "%s.swissprot.hits" % args.output
output_swissprot_blastp_hits_names = "%s.swissprot.hits_names" % args.output
output_gff = "%s.gff" % args.output

AUGUSTUS.threads = args.threads

AUGUSTUS.parallel_predict(args.species, args.input, output_gff, strand=args.strand, gene_model=args.gene_model,
                          output_gff3=True, other_options=args.other_options, config_dir=args.config_dir)
AUGUSTUS.extract_proteins_from_output(args.output, output_pep)

if args.pfam_db:
    HMMER3.threads = args.threads
    HMMER3.parallel_hmmscan(args.pfam_db, output_pep, num_of_seqs_per_scan=None, split_dir="splited_hmmscan_fasta/",
                            splited_output_dir="splited_hmmscan_output_dir",
                            tblout_outfile=None, domtblout_outfile=output_domtblout, pfamtblout_outfile=None,
                            splited_tblout_dir=None, splited_domtblout_dir="hmmscan_domtblout/")
    HMMER3.extract_dom_ids_hits_from_domtblout(output_domtblout, output_pfam_annotated_dom_ids)
    HMMER3.extract_dom_names_hits_from_domtblout(output_domtblout, output_pfam_annotated_dom_names)

    for directory in ("splited_hmmscan_fasta/", "splited_hmmscan_output_dir", "hmmscan_domtblout/"):
        shutil.rmtree(directory)

if args.swissprot_db:
    BLASTp.threads = args.threads
    BLASTp.parallel_blastp(output_pep, args.swissprot_db, evalue=0.0000001, output_format=6,
                           outfile=output_swissprot_blastp_hits, split_dir="splited_blastp_fasta",
                           splited_output_dir="splited_blastp_output_dir")
    BLASTp.extract_hits_from_tbl_output(output_swissprot_blastp_hits, output_swissprot_blastp_hits_names)

    for directory in ("splited_blastp_fasta", "splited_blastp_output_dir"):
        shutil.rmtree(directory)




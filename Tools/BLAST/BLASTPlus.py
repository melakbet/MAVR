#!/usr/bin/env python
__author__ = 'mahajrod'

import os
from subprocess import PIPE, Popen

from Tools.Abstract import Tool


class BLASTPlus(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "blastn", path=path, max_threads=max_threads)

    def make_blast_plus_db(self, input_file, mask_output_file, db_name):
        #makes BLAST database from fasta file
        os.system("dustmasker -in %s -infmt fasta -parse_seqids -outfmt maskinfo_asn1_bin -out %s"
                  % (input_file, mask_output_file))
        #creating database
        os.system("makeblastdb -in %s -input_type fasta -dbtype nucl -parse_seqids -mask_data %s -out %s -title '%s'"
                  % (input_file, mask_output_file, db_name, db_name))
        #cheking dqatabase
        os.system("blastdbcmd -db %s -info" % db_name)


class BLASTn(Tool):
    """
    USAGE
      blastn [-h] [-help] [-import_search_strategy filename]
        [-export_search_strategy filename] [-task task_name] [-db database_name]
        [-dbsize num_letters] [-gilist filename] [-seqidlist filename]
        [-negative_gilist filename] [-entrez_query entrez_query]
        [-db_soft_mask filtering_algorithm] [-db_hard_mask filtering_algorithm]
        [-subject subject_input_file] [-subject_loc range] [-query input_file]
        [-out output_file] [-evalue evalue] [-word_size int_value]
        [-gapopen open_penalty] [-gapextend extend_penalty]
        [-perc_identity float_value] [-xdrop_ungap float_value]
        [-xdrop_gap float_value] [-xdrop_gap_final float_value]
        [-searchsp int_value] [-max_hsps_per_subject int_value] [-penalty penalty]
        [-reward reward] [-no_greedy] [-min_raw_gapped_score int_value]
        [-template_type type] [-template_length int_value] [-dust DUST_options]
        [-filtering_db filtering_database]
        [-window_masker_taxid window_masker_taxid]
        [-window_masker_db window_masker_db] [-soft_masking soft_masking]
        [-ungapped] [-culling_limit int_value] [-best_hit_overhang float_value]
        [-best_hit_score_edge float_value] [-window_size int_value]
        [-off_diagonal_range int_value] [-use_index boolean] [-index_name string]
        [-lcase_masking] [-query_loc range] [-strand strand] [-parse_deflines]
        [-outfmt format] [-show_gis] [-num_descriptions int_value]
        [-num_alignments int_value] [-html] [-max_target_seqs num_sequences]
        [-num_threads int_value] [-remote] [-version]

    DESCRIPTION
       Nucleotide-Nucleotide BLAST 2.2.28+

    OPTIONAL ARGUMENTS
     -h
       Print USAGE and DESCRIPTION;  ignore all other parameters
     -help
       Print USAGE, DESCRIPTION and ARGUMENTS; ignore all other parameters
     -version
       Print version number;  ignore other arguments

     *** Input query options
     -query <File_In>
       Input file name
       Default = `-'
     -query_loc <String>
       Location on the query sequence in 1-based offsets (Format: start-stop)
     -strand <String, `both', `minus', `plus'>
       Query strand(s) to search against database/subject
       Default = `both'

     *** General search options
     -task <String, Permissible values: 'blastn' 'blastn-short' 'dc-megablast'
                    'megablast' 'rmblastn' >
       Task to execute
       Default = `megablast'
     -db <String>
       BLAST database name
        * Incompatible with:  subject, subject_loc
     -out <File_Out>
       Output file name
       Default = `-'
     -evalue <Real>
       Expectation value (E) threshold for saving hits
       Default = `10'
     -word_size <Integer, >=4>
       Word size for wordfinder algorithm (length of best perfect match)
     -gapopen <Integer>
       Cost to open a gap
     -gapextend <Integer>
       Cost to extend a gap
     -penalty <Integer, <=0>
       Penalty for a nucleotide mismatch
     -reward <Integer, >=0>
       Reward for a nucleotide match
     -use_index <Boolean>
       Use MegaBLAST database index
     -index_name <String>
       MegaBLAST database index name

     *** BLAST-2-Sequences options
     -subject <File_In>
       Subject sequence(s) to search
        * Incompatible with:  db, gilist, seqidlist, negative_gilist,
       db_soft_mask, db_hard_mask
     -subject_loc <String>
       Location on the subject sequence in 1-based offsets (Format: start-stop)
        * Incompatible with:  db, gilist, seqidlist, negative_gilist,
       db_soft_mask, db_hard_mask, remote

     *** Formatting options
     -outfmt <String>
       alignment view options:
         0 = pairwise,
         1 = query-anchored showing identities,
         2 = query-anchored no identities,
         3 = flat query-anchored, show identities,
         4 = flat query-anchored, no identities,
         5 = XML Blast output,
         6 = tabular,
         7 = tabular with comment lines,
         8 = Text ASN.1,
         9 = Binary ASN.1,
        10 = Comma-separated values,
        11 = BLAST archive format (ASN.1)

       Options 6, 7, and 10 can be additionally configured to produce
       a custom format specified by space delimited format specifiers.
       The supported format specifiers are:
            qseqid means Query Seq-id
               qgi means Query GI
              qacc means Query accesion
           qaccver means Query accesion.version
              qlen means Query sequence length
            sseqid means Subject Seq-id
         sallseqid means All subject Seq-id(s), separated by a ';'
               sgi means Subject GI
            sallgi means All subject GIs
              sacc means Subject accession
           saccver means Subject accession.version
           sallacc means All subject accessions
              slen means Subject sequence length
            qstart means Start of alignment in query
              qend means End of alignment in query
            sstart means Start of alignment in subject
              send means End of alignment in subject
              qseq means Aligned part of query sequence
              sseq means Aligned part of subject sequence
            evalue means Expect value
          bitscore means Bit score
             score means Raw score
            length means Alignment length
            pident means Percentage of identical matches
            nident means Number of identical matches
          mismatch means Number of mismatches
          positive means Number of positive-scoring matches
           gapopen means Number of gap openings
              gaps means Total number of gaps
              ppos means Percentage of positive-scoring matches
            frames means Query and subject frames separated by a '/'
            qframe means Query frame
            sframe means Subject frame
              btop means Blast traceback operations (BTOP)
           staxids means Subject Taxonomy ID(s), separated by a ';'
         sscinames means Subject Scientific Name(s), separated by a ';'
         scomnames means Subject Common Name(s), separated by a ';'
        sblastnames means Subject Blast Name(s), separated by a ';'
                 (in alphabetical order)
        sskingdoms means Subject Super Kingdom(s), separated by a ';'
                 (in alphabetical order)
            stitle means Subject Title
        salltitles means All Subject Title(s), separated by a '<>'
           sstrand means Subject Strand
             qcovs means Query Coverage Per Subject
           qcovhsp means Query Coverage Per HSP
       When not provided, the default value is:
       'qseqid sseqid pident length mismatch gapopen qstart qend sstart send
       evalue bitscore', which is equivalent to the keyword 'std'
       Default = `0'
     -show_gis
       Show NCBI GIs in deflines?
     -num_descriptions <Integer, >=0>
       Number of database sequences to show one-line descriptions for
       Not applicable for outfmt > 4
       Default = `500'
        * Incompatible with:  max_target_seqs
     -num_alignments <Integer, >=0>
       Number of database sequences to show alignments for
       Default = `250'
        * Incompatible with:  max_target_seqs
     -html
       Produce HTML output?

     *** Query filtering options
     -dust <String>
       Filter query sequence with DUST (Format: 'yes', 'level window linker', or
       'no' to disable)
       Default = `20 64 1'
     -filtering_db <String>
       BLAST database containing filtering elements (i.e.: repeats)
     -window_masker_taxid <Integer>
       Enable WindowMasker filtering using a Taxonomic ID
     -window_masker_db <String>
       Enable WindowMasker filtering using this repeats database.
     -soft_masking <Boolean>
       Apply filtering locations as soft masks
       Default = `true'
     -lcase_masking
       Use lower case filtering in query and subject sequence(s)?

     *** Restrict search or results
     -gilist <String>
       Restrict search of database to list of GI's
        * Incompatible with:  negative_gilist, seqidlist, remote, subject,
       subject_loc
     -seqidlist <String>
       Restrict search of database to list of SeqId's
        * Incompatible with:  gilist, negative_gilist, remote, subject,
       subject_loc
     -negative_gilist <String>
       Restrict search of database to everything except the listed GIs
        * Incompatible with:  gilist, seqidlist, remote, subject, subject_loc
     -entrez_query <String>
       Restrict search with the given Entrez query
        * Requires:  remote
     -db_soft_mask <String>
       Filtering algorithm ID to apply to the BLAST database as soft masking
        * Incompatible with:  db_hard_mask, subject, subject_loc
     -db_hard_mask <String>
       Filtering algorithm ID to apply to the BLAST database as hard masking
        * Incompatible with:  db_soft_mask, subject, subject_loc
     -perc_identity <Real, 0..100>
       Percent identity
     -culling_limit <Integer, >=0>
       If the query range of a hit is enveloped by that of at least this many
       higher-scoring hits, delete the hit
        * Incompatible with:  best_hit_overhang, best_hit_score_edge
     -best_hit_overhang <Real, (>=0 and =<0.5)>
       Best Hit algorithm overhang value (recommended value: 0.1)
        * Incompatible with:  culling_limit
     -best_hit_score_edge <Real, (>=0 and =<0.5)>
       Best Hit algorithm score edge value (recommended value: 0.1)
        * Incompatible with:  culling_limit
     -max_target_seqs <Integer, >=1>
       Maximum number of aligned sequences to keep
       Not applicable for outfmt <= 4
       Default = `500'
        * Incompatible with:  num_descriptions, num_alignments

     *** Discontiguous MegaBLAST options
     -template_type <String, `coding', `coding_and_optimal', `optimal'>
       Discontiguous MegaBLAST template type
        * Requires:  template_length
     -template_length <Integer, Permissible values: '16' '18' '21' >
       Discontiguous MegaBLAST template length
        * Requires:  template_type

     *** Statistical options
     -dbsize <Int8>
       Effective length of the database
     -searchsp <Int8, >=0>
       Effective length of the search space
     -max_hsps_per_subject <Integer, >=0>
       Override maximum number of HSPs per subject to save for ungapped searches
       (0 means do not override)
       Default = `0'

     *** Search strategy options
     -import_search_strategy <File_In>
       Search strategy to use
        * Incompatible with:  export_search_strategy
     -export_search_strategy <File_Out>
       File name to record the search strategy used
        * Incompatible with:  import_search_strategy

     *** Extension options
     -xdrop_ungap <Real>
       X-dropoff value (in bits) for ungapped extensions
     -xdrop_gap <Real>
       X-dropoff value (in bits) for preliminary gapped extensions
     -xdrop_gap_final <Real>
       X-dropoff value (in bits) for final gapped alignment
     -no_greedy
       Use non-greedy dynamic programming extension
     -min_raw_gapped_score <Integer>
       Minimum raw gapped score to keep an alignment in the preliminary gapped and
       traceback stages
     -ungapped
       Perform ungapped alignment only?
     -window_size <Integer, >=0>
       Multiple hits window size, use 0 to specify 1-hit algorithm
     -off_diagonal_range <Integer, >=0>
       Number of off-diagonals to search for the 2nd hit, use 0 to turn off
       Default = `0'

     *** Miscellaneous options
     -parse_deflines
       Should the query and subject defline(s) be parsed?
     -num_threads <Integer, >=1>
       Number of threads (CPUs) to use in the BLAST search
       Default = `1'
        * Incompatible with:  remote
     -remote
       Execute search remotely?
        * Incompatible with:  gilist, seqidlist, negative_gilist, subject_loc,
       num_threads
    """
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "blastn", path=path, max_threads=max_threads)


class BLASTp(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "blastp", path=path, max_threads=max_threads)


class DustMasker(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "dustmasker", path=path, max_threads=max_threads)


class MakeBLASTDb(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "makeblastdb", path=path, max_threads=max_threads)


class BLASTDbCmd(Tool):
    def __init__(self, path="", max_threads=4):
        Tool.__init__(self, "blastdbcmd", path=path, max_threads=max_threads)

if __name__ == "__main__":

    blast_plus = BLASTPlus()
    workdir = "/home/mahajrod/genetics/nxf/annotation/test/Dmel/nxf1/"
    os.chdir(workdir)
    blast_plus.make_blast_plus_db("/home/mahajrod/genetics/nxf/annotation/test/Dmel/nxf1/dmel-all-chromosome-r5.54.fasta",
                                  "dmel_all_chromosome.asnb", "dmel_all_chromosome")
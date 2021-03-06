#!/usr/bin/env python

__author__ = 'mahajrod'

from Tools.GATK.Abstract import GATKTool


class BaseRecalibrator(GATKTool):

    def get_recalibration_table(self, reference, alignment, output_table="", known_sites_vcf=None):

        # TODO: add rest of  options
        options = ""
        options += " -R %s" % reference
        options += " -I %s" % alignment
        options += " -nct %i" % self.threads
        options += " -knownSites" + " -knownSites".join(known_sites_vcf) if isinstance(known_sites_vcf, list) else " -knownSites %s" % known_sites_vcf
        options += " -o %s" % output_table

        self.execute(options, cmd="-T BaseRecalibrator")

if __name__ == "__main__":
    import os
    workdir = "/media/mahajrod/d9e6e5ee-1bf7-4dba-934e-3f898d9611c8/Data/Alsu/fastq/001/alignment_tmap_Alsu24mc"
    os.chdir(workdir)
    #gatk_dir =
    reference = "/media/mahajrod/d9e6e5ee-1bf7-4dba-934e-3f898d9611c8/Data/Alsu/reference/Alsu24mc/Alsu24mc.fasta"
    alignment = "/media/mahajrod/d9e6e5ee-1bf7-4dba-934e-3f898d9611c8/Data/Alsu/fastq/001/alignment_tmap_Alsu24mc/001_trimmed_sorted_rm_pcr_chrom_corrected.bam"
    corrected_alignment = "001_trimmed_sorted_rm_pcr_chrom_corrected.bam"
    BaseRecalibrator = BaseRecalibrator(jar_path="/home/mahajrod/Repositories/genetic/NGS_tools/GenomeAnalysisTK-3.2-0")
    BaseRecalibrator.get_recalibration_table(reference, alignment)

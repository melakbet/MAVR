#!/usr/bin/env python
import os, shutil

from Tools.Filter import Cookiecutter, Trimmomatic, FaCut
from Routines import FileRoutines
from Parsers.FaCut import FaCutReport
from Parsers.Coockiecutter import CoockiecutterReport


class FilteringPipeline:
    def __init__(self):
        pass

    @staticmethod
    def prepare_directories(output_directory, sample_list):
        merged_raw_dir = "%s/merged/" % output_directory
        filtered_dir = "%s/filtered/" % output_directory
        filtering_stat_dir = "%s/filtered_stat/" % output_directory
        coockie_filtered_dir = "%s/coockiecutter/" % filtered_dir
        coockie_trimmomatic_filtered_dir = "%s/coockiecutter_trimmomatic/" % filtered_dir
        coockie_trimmomatic_quality_filtered_dir = "%s/coockiecutter_trimmomatic_quality/" % filtered_dir
        final_filtered_dir = "%s/final/" % filtered_dir

        FileRoutines.save_mkdir(filtered_dir)
        for directory in merged_raw_dir, coockie_filtered_dir, coockie_trimmomatic_filtered_dir, coockie_trimmomatic_quality_filtered_dir, final_filtered_dir, filtering_stat_dir:
            FileRoutines.save_mkdir(directory)
            for sample in sample_list:
                FileRoutines.save_mkdir("%s/%s" % (directory, sample))

    @staticmethod
    def get_sample_list(samples_directory):
        samples = sorted(os.listdir(samples_directory))
        sample_list = []
        for sample in samples:
            if os.path.isdir("%s/%s" % (samples_directory, sample)):
                sample_list.append(sample)
        return sample_list

    @staticmethod
    def combine_files(samples_directory, sample, output_directory):
        sample_dir = "%s/%s/" % (samples_directory, sample)
        filetypes, forward_files, reverse_files = FileRoutines.make_lists_forward_and_reverse_files(sample_dir)
        if len(filetypes) == 1:
            if "fq.gz" in filetypes:
                command = "zcat"
            elif "fq.bz2" in filetypes:
                command = "bzcat"
            else:
                command = "cat"

            os.system("%s %s > %s/%s_1.fq" % (command, " ".join(forward_files), output_directory, sample))
            os.system("%s %s > %s/%s_2.fq" % (command, " ".join(reverse_files), output_directory, sample))
        else:
            raise IOError("Extracting from mix of archives in not implemented yet")

    def filter(self, samples_directory, output_directory, adapter_fragment_file, trimmomatic_adapter_file,
               samples_to_handle=None, threads=4, trimmomatic_dir="", coockiecutter_dir="", facut_dir="",
               mismatch_number=2, pe_reads_score=30, se_read_score=10,
               min_adapter_len=1, sliding_window_size=None,
               average_quality_threshold=15,
               leading_base_quality_threshold=None, trailing_base_quality_threshold=None,
               crop_length=None, head_crop_length=None, min_len=50,
               base_quality="phred33", read_name_type="illumina", remove_intermediate_files=False):

        Cookiecutter.path = coockiecutter_dir
        Trimmomatic.jar_path = trimmomatic_dir
        Trimmomatic.threads = threads
        FaCut.path = facut_dir

        merged_raw_dir = "%s/merged/" % output_directory
        filtered_dir = "%s/filtered/" % output_directory
        coockie_filtered_dir = "%s/coockiecutter/" % filtered_dir
        coockie_trimmomatic_filtered_dir = "%s/coockiecutter_trimmomatic/" % filtered_dir
        coockie_trimmomatic_quality_filtered_dir = "%s/coockiecutter_trimmomatic_quality/" % filtered_dir
        final_filtered_dir = "%s/final/" % filtered_dir
        filtering_stat_dir = "%s/filtered_stat/" % output_directory

        sample_list = samples_to_handle if samples_to_handle else self.get_sample_list(samples_directory)
        self.prepare_directories(output_directory, sample_list)
        for sample in sample_list:
            print "Handling sample %s" % sample
            merged_raw_sample_dir = "%s/%s/" % (merged_raw_dir, sample)
            merged_forward_reads = "%s/%s_1.fq" % (merged_raw_sample_dir, sample)
            merged_reverse_reads = "%s/%s_2.fq" % (merged_raw_sample_dir, sample)

            coockie_filtered_sample_dir = "%s/%s/" % (coockie_filtered_dir, sample)
            coockie_stats = "%s/%s.coockiecutter.stats" % (coockie_filtered_sample_dir, sample)

            coockie_trimmomatic_filtered_sample_dir = "%s/%s/" % (coockie_trimmomatic_filtered_dir, sample)

            coockie_trimmomatic_quality_filtered_sample_dir = "%s/%s/" % (coockie_trimmomatic_quality_filtered_dir, sample)
            final_filtered_sample_dir = "%s/%s/" % (final_filtered_dir, sample)
            filtering_stat_sample_dir = "%s/%s" % (filtering_stat_dir, sample)

            self.combine_files(samples_directory, sample, merged_raw_sample_dir)
            """
            Cookiecutter.rm_reads(adapter_fragment_file, merged_forward_reads, coockie_stats,
                                  right_reads=merged_reverse_reads,
                                  out_dir=coockie_filtered_sample_dir, use_dust_filter=False,
                                  dust_cutoff=None, dust_window_size=None, use_N_filter=False,
                                  read_length_cutoff=None, polyGC_length_cutoff=None)
            """
            coockiecutter_report = CoockiecutterReport(coockie_stats)

            os.system("cp %s %s" % (coockie_stats, filtering_stat_sample_dir))

            coockie_filtered_paired_forward_reads = "%s/%s_1.ok.fastq" % (coockie_filtered_sample_dir, sample)
            coockie_filtered_paired_reverse_reads = "%s/%s_2.ok.fastq" % (coockie_filtered_sample_dir, sample)
            # se reads produced by Coockiecutter are ignored now!!

            coockie_trimmomatic_filtered_sample_dir = "%s/%s/" % (coockie_trimmomatic_filtered_dir, sample)
            trimmomatic_output_prefix = "%s/%s" % (coockie_trimmomatic_filtered_sample_dir, sample)
            trimmomatic_log = "%s.trimmomatic.log" % trimmomatic_output_prefix
            """
            Trimmomatic.filter(coockie_filtered_paired_forward_reads, trimmomatic_output_prefix, output_extension="fq",
                               right_reads=coockie_filtered_paired_reverse_reads,
                               adapters_file=trimmomatic_adapter_file,
                               mismatch_number=mismatch_number, pe_reads_score=pe_reads_score,
                               se_read_score=se_read_score,
                               min_adapter_len=min_adapter_len, sliding_window_size=sliding_window_size,
                               average_quality_threshold=average_quality_threshold,
                               leading_base_quality_threshold=leading_base_quality_threshold,
                               trailing_base_quality_threshold=trailing_base_quality_threshold,
                               crop_length=crop_length, head_crop_length=head_crop_length, min_length=min_len,
                               logfile=trimmomatic_log,
                               base_quality=base_quality)
            """
            os.system("cp %s %s" % (trimmomatic_log, filtering_stat_sample_dir))

            coockie_trimmomatic_filtered_paired_forward_reads = "%s/%s_1.pe.fq" % (coockie_trimmomatic_filtered_sample_dir, sample)
            coockie_trimmomatic_filtered_paired_reverse_reads = "%s/%s_2.pe.fq" % (coockie_trimmomatic_filtered_sample_dir, sample)

            final_forward_reads = "%s/%s.final_1.fastq" % (final_filtered_sample_dir, sample)
            final_reverse_reads = "%s/%s.final_2.fastq" % (final_filtered_sample_dir, sample)

            if sliding_window_size is None:
                facut_output_prefix = "%s/%s" % (coockie_trimmomatic_quality_filtered_sample_dir, sample)
                facut_stat_file = "%s.facut.stat" % facut_output_prefix
                """
                FaCut.filter_by_mean_quality(average_quality_threshold,
                                             coockie_trimmomatic_filtered_paired_forward_reads,
                                             coockie_trimmomatic_filtered_paired_reverse_reads,
                                             facut_output_prefix, quality_type=base_quality,
                                             stat_file=facut_stat_file, name_type=read_name_type)
                """
                facut_report = FaCutReport(facut_stat_file)

                facut_filtered_forward_reads = "%s_1.pe.fq" % facut_output_prefix
                facut_filtered_reverse_reads = "%s_2.pe.fq" % facut_output_prefix
                os.system("cp %s %s" % (facut_stat_file, filtering_stat_sample_dir))
                os.system("ln %s %s" % (facut_filtered_forward_reads, final_forward_reads))
                os.system("ln %s %s" % (facut_filtered_reverse_reads, final_reverse_reads))

            else:
                os.system("ln %s %s" % (coockie_trimmomatic_filtered_paired_forward_reads, final_forward_reads))
                os.system("ln %s %s" % (coockie_trimmomatic_filtered_paired_reverse_reads, final_reverse_reads))

            if remove_intermediate_files:
                shutil.rmtree(coockie_filtered_dir)
                shutil.rmtree(coockie_trimmomatic_filtered_dir)
                shutil.rmtree(coockie_trimmomatic_quality_filtered_dir)

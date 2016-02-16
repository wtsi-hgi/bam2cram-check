import os
import subprocess
import logging
import re

from checks import utils

"""
- works only for lossless (checks that the stats are identical)
"""

# module add hgi/samtools/git-latest
class RunSamtoolsCommands:
    @classmethod
    def _run_subprocess(cls, args_list):
        proc = subprocess.run(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        utils.log_error(args_list, proc.stderr, proc.returncode)
        return proc.stdout

    @classmethod
    def run_samtools_quickcheck(cls, fpath):
        return cls._run_subprocess(['samtools', 'quickcheck', '-v', fpath])

    @classmethod
    def get_samtools_flagstat_output(cls, fpath):
        return cls._run_subprocess(['samtools', 'flagstat', fpath])

    @classmethod
    def get_samtools_stats_output(cls, fpath):
        return cls._run_subprocess(['samtools', 'stats', fpath])


class HandleSamtoolsStats:

    @classmethod
    def _get_stats(cls, stats_fpath):
        if stats_fpath and os.path.isfile(stats_fpath):
            return utils.read_from_file(stats_fpath)
        return None
        #raise ValueError("No stats file found: %s" % str(stats_fpath))

    @classmethod
    def _generate_stats(cls, data_fpath):
        if not data_fpath or not os.path.isfile(data_fpath):
            raise ValueError("Can't generate stats from a non-existing file: %s" % str(data_fpath))
        return RunSamtoolsCommands.get_samtools_stats_output(data_fpath)

    @classmethod
    def _save_stats(cls, stats, stats_fpath):    # =data_fpath+'.stats'
        if not stats or not stats_fpath:
            raise ValueError("You must provide both stats and stats file path for saving the stats to a file."
                         " Received stats = %s and stats fpath = %s" % (str(stats), str(stats_fpath)))
        return utils.write_to_file(stats_fpath, stats)

    @classmethod
    def fetch_and_persist_stats(cls, fpath):
        if not fpath or not os.path.isfile(fpath):
            raise ValueError("You need to give a valid file path if you want the stats")
        stats_fpath = fpath + ".stats"
        stats = HandleSamtoolsStats._get_stats(stats_fpath) # TODO: try - catch ValueError
        if not stats:
            stats = HandleSamtoolsStats._generate_stats(fpath)
            HandleSamtoolsStats._save_stats(stats, stats_fpath)
        return stats

    # @classmethod
    # def create_and_save_stats(cls, stats_fpath, data_fpath, ):
    #     stats = RunSamtoolsCommands.get_samtools_stats_output(data_fpath)
    #     utils.write_to_file(stats_fpath, stats)
    #     return stats
    #
    # @classmethod
    # def get_or_create_stats(cls, stats_fpath, data_fpath=None):
    #     if not stats_fpath and not data_fpath:
    #         raise ValueError("Insufficient information, the parameters stats_file and data_file can't both be None.")
    #     if stats_fpath:
    #         if not os.path.isfile(stats_fpath):
    #             raise ValueError("Stats filepath is not a valid path: %s" % stats_fpath)
    #         return utils.read_from_file(stats_fpath)
    #     elif data_fpath:
    #         if not os.path.isfile(data_fpath):
    #             raise ValueError("Data filepath is not a valid path: %s" % data_fpath)
    #         return cls.create_and_save_stats(stats_fpath, data_fpath)

    @classmethod
    def extract_seq_checksum_from_stats(cls, stats: str) -> str:
        for line in stats.split('\n'):
            if re.search('^CHK', line):
                return line
        return None


class CompareStatsForFiles:
    @classmethod
    def compare_flagstats(cls, flagstat_b, flagstat_c):
        errors = []
        if flagstat_b != flagstat_c:
            logging.error("FLAGSTAT DIFFERENT:\n %s then:\n %s " % (flagstat_b, flagstat_c))
            errors.append("FLAGSTAT DIFFERENT:\n %s then:\n %s " % (flagstat_b, flagstat_c))
        return errors

    @classmethod
    def compare_stats_by_sequence_checksum(cls, stats_b, stats_c):
        errors = []
        # stats_path_b = bam_path + ".stats"
        #
        #
        # stats_c = HandleSamtoolsStats._get_stats(stats_path_c)
        # if not stats_c:
        #     stats_c = HandleSamtoolsStats._generate_stats(cram_path)
        #     HandleSamtoolsStats._save_stats(stats_c, stats_path_c)

        # stats_b = HandleSamtoolsStats.get_or_create_stats(stats_path_b, bam_path)
        # stats_c = HandleSamtoolsStats.get_or_create_stats(stats_path_c, cram_path)

        if not stats_b or not stats_c:
            errors.append("You need to provide both BAM and CRAM stats for cmparison")
            return errors

        chk_b = HandleSamtoolsStats.extract_seq_checksum_from_stats(stats_b)
        chk_c = HandleSamtoolsStats.extract_seq_checksum_from_stats(stats_c)

        if not chk_b:
            errors.append("For some reason there is no CHK line in the samtools stats")
            logging.error("For some reason there is no CHK line in the samtools stats")
        if not chk_c:
            errors.append("For some reason there is no CHK line in the samtools stats")
            logging.error("For some reason there is no CHK line in the samtools stats")

        if chk_b != chk_c:
            errors.append("STATS SEQUENCE CHECKSUM DIFFERENT: %s and %s" % (chk_b, chk_c))
            logging.error("STATS SEQUENCE CHECKSUM DIFFERENT: %s and %s" % (chk_b, chk_c))
        return errors

    # TODO: check on flagstat and stats that they exist and raise errors if they dont
    @classmethod
    def compare_bam_and_cram_by_statistics(cls, bam_path, cram_path):
        errors = []
        flagstat_b = RunSamtoolsCommands.get_samtools_flagstat_output(bam_path)
        flagstat_c = RunSamtoolsCommands.get_samtools_flagstat_output(cram_path)
        errors.extend(cls.compare_flagstats(flagstat_b, flagstat_c))

        stats_b = HandleSamtoolsStats.fetch_and_persist_stats(bam_path)
        stats_c = HandleSamtoolsStats.fetch_and_persist_stats(cram_path)
        errors.extend(cls.compare_stats_by_sequence_checksum(stats_b, stats_c))
        return errors





import os
import argparse
import subprocess
import logging
import re

import utils
"""
- works only for lossless (checks that the stats are identical)
"""

# module add hgi/samtools/git-latest
class RunSamtoolsComands:
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
    def create_and_save_stats(cls, stats_fpath, data_fpath, ):
        stats = RunSamtoolsComands.get_samtools_stats_output(data_fpath)
        utils.write_to_file(stats_fpath, stats)
        return stats

    @classmethod
    def get_or_create_stats(cls, stats_fpath, data_fpath=None):
        if not stats_fpath and not data_fpath:
            raise ValueError("Insufficient information, the parameters stats_file and data_file can't both be None.")
        if stats_fpath:
            if not os.path.isfile(stats_fpath):
                raise ValueError("Stats filepath is not a valid path: %s" % stats_fpath)
            return utils.read_from_file(stats_fpath)
        elif data_fpath:
            if not os.path.isfile(data_fpath):
                raise ValueError("Data filepath is not a valid path: %s" % data_fpath)
            return cls.create_and_save_stats(stats_fpath, data_fpath)

    @classmethod
    def get_chk_from_stats(cls, stats: str) -> str:
        for line in stats.split('\n'):
            if re.search('^CHK', line):
                return line
        return None


class CompareStatsForFiles:
    @classmethod
    def compare_flagstats(cls, bam_path, cram_path):
        errors = []
        flagstat_b = RunSamtoolsComands.get_samtools_flagstat_output(bam_path)
        flagstat_c = RunSamtoolsComands.get_samtools_flagstat_output(cram_path)
        if flagstat_b != flagstat_c:
            logging.error("FLAGSTAT DIFFERENT for %s : %s and %s : %s " % (bam_path, flagstat_b, cram_path, flagstat_c))
            errors.append("FLAGSTAT DIFFERENT for %s : %s and %s : %s " % (bam_path, flagstat_b, cram_path, flagstat_c))
        return errors

    @classmethod
    def compare_sequence_checksum(cls, bam_path, cram_path):
        errors = []
        stats_path_b = bam_path + ".stats"
        stats_path_c = cram_path + ".stats"

        stats_b = HandleSamtoolsStats.get_or_create_stats(stats_path_b, bam_path)
        stats_c = HandleSamtoolsStats.get_or_create_stats(stats_path_c, cram_path)

        chk_b = HandleSamtoolsStats.get_chk_from_stats(stats_b)
        chk_c = HandleSamtoolsStats.get_chk_from_stats(stats_c)

        if not chk_b:
            errors.append(("For some reason there is no CHK line in the samtools stats of %s " % bam_path))
            logging.error("For some reason there is no CHK line in the samtools stats of %s " % bam_path)
        if not chk_c:
            errors.append(("For some reason there is no CHK line in the samtools stats of %s " % cram_path))
            logging.error("For some reason there is no CHK line in the samtools stats of %s " % cram_path)

        if chk_b != chk_c:
            errors.append("STATS SEQUENCE CHECKSUM DIFFERENT for %s: %s and %s: %s" % (bam_path, chk_b, cram_path, chk_c))
            logging.error("STATS SEQUENCE CHECKSUM DIFFERENT for %s: %s and %s: %s" % (bam_path, chk_b, cram_path, chk_c))
        return errors

    @classmethod
    def compare_bam_and_cram_statistics(cls, bam_path, cram_path):
        errors = []
        errors.extend(cls.compare_flagstats(bam_path, cram_path))
        errors.extend(cls.compare_sequence_checksum(bam_path, cram_path))
        return errors



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', help="File path to the BAM file", required=True)
    parser.add_argument('-c', help="File path to the CRAM file", required=True)
    parser.add_argument('-e', help="File path to the error file", required=False)
    parser.add_argument('--log', help="File path to the log file", required=False)
    parser.add_argument('-v', action='count')
    return parser.parse_args()


 # TODO: add check_if_writable here
# To make the default logging to be stdout
def main():
    args = parse_args()
    log_level = (logging.CRITICAL - 10 * args.v) if args.v else logging.INFO
    log_file = args.log if args.log else 'compare_b2c.log'
    logging.basicConfig(level=log_level, format='%(levelname)s - %(asctime)s %(message)s', filename=log_file)
    if args.b and args.c:
        bam_path = args.b
        cram_path = args.c

        if not os.path.isfile(bam_path):
            logging.error("This is not a file path: %s" % bam_path)
            raise ValueError("This is not a file path: %s")
        if not os.path.isfile(cram_path):
            logging.error("This is not a file path: %s" %cram_path)
            raise ValueError("This is not a file path: %s")

        RunSamtoolsComands.run_samtools_quickcheck(bam_path)
        RunSamtoolsComands.run_samtools_quickcheck(cram_path)
        errors = CompareStatsForFiles.compare_bam_and_cram_statistics(bam_path, cram_path)

        if errors:
            if args.e:
                err_f = open(args.e, 'w')
                for err in errors:
                    err_f.write(err + '\n')
                err_f.close()
            else:
                print(errors)


if __name__ == '__main__':
    main()

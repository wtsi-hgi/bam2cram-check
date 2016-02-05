

import os
import argparse
import subprocess
import logging
import re

"""
- works only for lossless (checks that the stats are identical)
"""

# module add hgi/samtools/git-latest

def run_subprocess(args_list):
    proc = subprocess.run(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    log_error(args_list, proc.stderr, proc.returncode)
    return proc.stdout


def run_samtools_quickcheck(fpath):
    return run_subprocess(['samtools', 'quickcheck', '-v', fpath])


def get_samtools_flagstat_output(fpath):
    return run_subprocess(['samtools', 'flagstat', fpath])


def get_samtools_stats_output(fpath):
    return run_subprocess(['samtools', 'stats', fpath])


def get_chk_from_stats(stats: str) -> str:
    for line in stats.split('\n'):
        if re.search('^CHK', line):
            return line
    return None


def create_and_save_stats(stats_fpath, data_fpath, ):
    stats = get_samtools_stats_output(data_fpath)
    write_to_file(stats_fpath, stats)
    return stats


def get_or_create_stats(stats_fpath, data_fpath=None):
    if not stats_fpath and not data_fpath:
        raise ValueError("Insufficient information, the parameters stats_file and data_file can't both be None.")
    if stats_fpath:
        if not os.path.isfile(stats_fpath):
            raise ValueError("Stats filepath is not a valid path: %s" % stats_fpath)
        return read_from_file(stats_fpath)
    elif data_fpath:
        if not os.path.isfile(data_fpath):
            raise ValueError("Data filepath is not a valid path: %s" % data_fpath)
        return create_and_save_stats(stats_fpath, data_fpath)


def compare_flagstats(bam_path, cram_path):
    errors = []
    flagstat_b = get_samtools_flagstat_output(bam_path)
    flagstat_c = get_samtools_flagstat_output(cram_path)
    if flagstat_b != flagstat_c:
        logging.error("FLAGSTAT DIFFERENT for %s : %s and %s : %s " % (bam_path, flagstat_b, cram_path, flagstat_c))
        errors.append("FLAGSTAT DIFFERENT for %s : %s and %s : %s " % (bam_path, flagstat_b, cram_path, flagstat_c))
    return errors


def compare_sequence_checksum(bam_path, cram_path):
    errors = []
    stats_path_b = bam_path + ".stats"
    stats_path_c = cram_path + ".stats"

    stats_b = get_or_create_stats(stats_path_b, bam_path)
    stats_c = get_or_create_stats(stats_path_c, cram_path)

    chk_b = get_chk_from_stats(stats_b)
    chk_c = get_chk_from_stats(stats_c)

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


def compare_bam_and_cram_statistics(bam_path, cram_path):
    errors = []
    errors.extend(compare_flagstats(bam_path, cram_path))
    errors.extend(compare_sequence_checksum(bam_path, cram_path))
    return errors


def run_checks(fpaths):
    for fpath in fpaths:
        run_samtools_quickcheck(fpath)


def log_error(cmd_str, stderr, exit_code):
    if stderr:
        if exit_code != 0:
            logging.error("%s exited with code: %s and threw an error: %s " % (cmd_str, exit_code, stderr))
        else:
            logging.error("%s had exit status 0, but threw an error: %s " % (cmd_str, stderr))
    elif exit_code != 0:
        logging.error("%s had no error, but exit code is non zero: %s" % (cmd_str, exit_code))
    else:
        logging.info("Ran successfully %s" % cmd_str)


def read_from_file(fpath):
    with open(fpath) as myfile:
        return myfile.read()


def write_to_file(fpath, text):
    f = open(fpath, 'w')
    f.write(text)
    f.close()

def check_path_writable(fpath):
    if os.path.isdir(fpath):
        if os.access(fpath, os.W_OK):
            return True
        return False
    else:
        if os.path.exists(fpath):
            if os.access(fpath, os.W_OK):
                return True
            return False
        else:
            parent_dir = os.path.dirname(fpath)
            if os.access(parent_dir, os.W_OK):
                return True
            return Flase



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', help="File path to the BAM file", required=True)
    parser.add_argument('-c', help="File path to the CRAM file", required=True)
    parser.add_argument('-e', help="File path to the error file", required=False)
    parser.add_argument('--log', help="File path to the log file", required=False)
    parser.add_argument('-v', action='count')
    return parser.parse_args()

 
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

        run_checks([bam_path, cram_path])
        errors = compare_bam_and_cram_statistics(bam_path, cram_path)

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

import mock
import unittest


class TestGetCHK(unittest.TestCase):

    def test_get_chk_from_stats_1(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\nCHK     1bfca46a        2046405a        f4f56eb9\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = "CHK     1bfca46a        2046405a        f4f56eb9"
        actual_result = get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_2(self):
        stats = ""
        wanted_result = None
        actual_result = get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_3(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = None
        actual_result = get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

class TestCheckPathWritable(unittest.TestCase):

    @mock.path('os')
    @mock.path('os.path')
    def test_check_path_writable_1(self, mock_path, mock_os):
        mock_path.exists.return_value = False
        self.assertFalse(check_path_writable('some_path'))
        # dir_path = os.getcwd()
        # self.assertTrue(check_path_writable(os.path.join(dir_path, 'test')))

# def check_path_writable(fpath):
#     if os.path.isdir(fpath):
#         if os.access(fpath, os.W_OK):
#             return True
#         return False
#     else:
#         if os.path.exists(fpath):
#             if os.access(fpath, os.W_OK):
#                 return True
#             return False
#         else:
#             parent_dir = os.path.dirname(fpath)
#             if os.access(parent_dir, os.W_OK):
#                 return True
#             return Flase
#
"""
Copyright (C) 2016  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of bam2cram-check

bam2cram-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Feb 10, 2016.
"""
import os
import argparse
import logging
from checks.stats_checks import RunSamtoolsCommands, CompareStatsForFiles

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

        RunSamtoolsCommands.run_samtools_quickcheck(bam_path)
        RunSamtoolsCommands.run_samtools_quickcheck(cram_path)
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

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

This file has been created on Feb 09, 2016.
"""
import logging
import os


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
    with open(fpath) as f:
        return f.read()


def write_to_file(fpath, text):
    with open(fpath, 'w') as f:
        f.write(text)
    return True


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
            return False


def compare_mtimestamp(fpath1, fpath2):
    if not fpath2 or not fpath1:
        raise ValueError("Both parameters neeed to be not None")
    if not os.path.isfile(fpath1) or not can_read_file(fpath1):
        raise IOError("The file %s either doesn't exist or I can't access it" % fpath1)
    if not os.path.isfile(fpath2) or not can_read_file(fpath2):
        raise IOError("The file %s either doesn't exist or I can't access it" % fpath2)

    tstamp1 = os.path.getmtime(fpath1)
    tstamp2 = os.path.getmtime(fpath2)
    print("Tstamp1: %s, tstamp2: %s" % (tstamp1, tstamp2))
    if tstamp1 - tstamp2 < 0:
        return -1
    elif tstamp1 - tstamp2 > 0:
        return 1
    return 0


def can_read_file(fpath):
    return os.access(fpath, os.R_OK)


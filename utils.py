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
            return False


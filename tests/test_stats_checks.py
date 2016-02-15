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

import unittest
import mock
from checks import stats_checks

# class RunSamtoolsComands:
#     @classmethod
#     def _run_subprocess(cls, args_list):
#         proc = subprocess.run(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#         utils.log_error(args_list, proc.stderr, proc.returncode)
#         return proc.stdout
#
#     @classmethod
#     def run_samtools_quickcheck(cls, fpath):
#         return cls._run_subprocess(['samtools', 'quickcheck', '-v', fpath])
#
#     @classmethod
#     def get_samtools_flagstat_output(cls, fpath):
#         return cls._run_subprocess(['samtools', 'flagstat', fpath])
#
#     @classmethod
#     def get_samtools_stats_output(cls, fpath):
#         return cls._run_subprocess(['samtools', 'stats', fpath])
#


import subprocess
from collections import namedtuple
class TestRunSamtoolsCommands(unittest.TestCase):

    @mock.patch('checks.stats_checks.subprocess.run')
    def test_run_subprocess_1(self, mock_subproc):
        some_obj = namedtuple('some_obj', ['stdout', 'stderr', 'returncode'])
        mock_subproc.return_value = some_obj(stdout='OK', stderr=None, returncode=0)
        result = stats_checks.RunSamtoolsCommands._run_subprocess(['samtools', 'quickcheck', 'mybam'])
        self.assertEqual(result, 'OK')
        mock_subproc.assert_called_with(['samtools', 'quickcheck', 'mybam'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

    @mock.patch('checks.stats_checks.subprocess.run')
    @mock.patch('checks.stats_checks.utils.log_error')
    def test_run_subprocess_2(self, mock_log_error, mock_run):
        some_obj = namedtuple('some_obj', ['stdout', 'stderr', 'returncode'])
        mock_run.return_value = some_obj(stdout='OK', stderr=None, returncode=0)
        stats_checks.RunSamtoolsCommands._run_subprocess(['samtools', 'quickcheck', 'mybam'])
        mock_log_error.assert_called_with(['samtools', 'quickcheck', 'mybam'], None, 0)


    @mock.patch('checks.stats_checks.subprocess.run')
    @mock.patch('checks.stats_checks.utils.log_error')
    def test_run_subprocess_3(self, mock_log_error, mock_run):
        some_obj = namedtuple('some_obj', ['stdout', 'stderr', 'returncode'])
        mock_run.return_value = some_obj(stdout='ERROR reading', stderr=None, returncode=1)
        stats_checks.RunSamtoolsCommands._run_subprocess(['samtools', 'quickcheck', 'mybam'])
        mock_log_error.assert_called_with(['samtools', 'quickcheck', 'mybam'], None, 1)

    @mock.patch('checks.stats_checks.RunSamtoolsCommands._run_subprocess')
    def test_run_samtools_quickcheck_1(self, mock_subproc):
        stats_checks.RunSamtoolsCommands.run_samtools_quickcheck('some_path')
        mock_subproc.assert_called_with(['samtools', 'quickcheck', '-v', 'some_path'])

    @mock.patch('checks.stats_checks.RunSamtoolsCommands._run_subprocess')
    def test_get_samtools_flagstat_output_1(self, mock_subproc):
        stats_checks.RunSamtoolsCommands.get_samtools_flagstat_output('some_path')
        mock_subproc.assert_called_with(['samtools', 'flagstat', 'some_path'])

    @mock.patch('checks.stats_checks.RunSamtoolsCommands._run_subprocess')
    def test_get_samtools_stats_output_1(self, mock_subproc):
        mock_subproc.return_value = 'some_stats'
        result = stats_checks.RunSamtoolsCommands.get_samtools_stats_output('some_path')
        mock_subproc.assert_called_with(['samtools', 'stats', 'some_path'])
        self.assertEqual(result, 'some_stats')


class TestHandleSamtoolsStats(unittest.TestCase):

    def test_get_chk_from_stats_1(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\nCHK     1bfca46a        2046405a        f4f56eb9\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = "CHK     1bfca46a        2046405a        f4f56eb9"
        actual_result = stats_checks.HandleSamtoolsStats.extract_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_2(self):
        stats = ""
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.extract_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_3(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.extract_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    @mock.patch('checks.utils.write_to_file')
    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_stats_output')
    def test_create_and_save_stats_1(self, mock_stats, mock_write_f):
        mock_stats.return_value = 'some_stats'
        result = stats_checks.HandleSamtoolsStats.create_and_save_stats('stats_path', 'data_path')
        mock_write_f.assume_called_with('stats_path', 'data_stats')
        self.assertEqual(result, 'some_stats')

    def test_get_or_create_stats_1(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.get_or_create_stats, None, None)
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.get_or_create_stats, 'some_path', None)
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.get_or_create_stats, None, 'some_path')

    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.utils.read_from_file')
    def test_get_or_create_stats_2(self, mock_read_f, mock_path):
        mock_read_f.return_value = 'stats_read_from_file'
        mock_path.return_value = True
        result = stats_checks.HandleSamtoolsStats.get_or_create_stats('some_path', None)
        self.assertEqual(result, 'stats_read_from_file')

    @mock.patch('checks.stats_checks.HandleSamtoolsStats.create_and_save_stats')
    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.utils.read_from_file')
    def test_get_or_create_stats_3(self, mock_read_f, mock_path, mock_stats):
        mock_read_f.return_value = 'stats_read_from_file'
        mock_path.isfile.return_value = True
        mock_stats.return_value = 'some_stats'
        result = stats_checks.HandleSamtoolsStats.get_or_create_stats(None, 'some_path')
        self.assertEqual(result, 'some_stats')



class TestCompareStatsForFiles(unittest.TestCase):

    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_flagstat_output')
    def test_compare_flagstats(self, mock_flagst):
        flagstat1 = "268505766 + 0 in total (QC-passed reads + QC-failed reads)\n0 + 0 secondary\n0 + 0 supplementary\n30981933 + 0 duplicates\n266920133 + 0 mapped (99.41% : N/A)\n268505766 + 0 paired in sequencing\n134252883 + 0 read1\n134252883 + 0 read2\n261775882 + 0 properly paired (97.49% : N/A)\n265641920 + 0 with itself and mate mapped\n1278213 + 0 singletons (0.48% : N/A)\n557330 + 0 with mate mapped to a different chr\n440283 + 0 with mate mapped to a different chr (mapQ>=5)\n"
        #flagstat2 = ""
        mock_flagst.side_effect = [flagstat1, flagstat1]
        self.assertListEqual([], stats_checks.CompareStatsForFiles.compare_files_by_flagstats('blah1', "blah2"))

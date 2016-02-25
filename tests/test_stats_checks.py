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

import os
from unittest import mock, TestCase, skip
from checks import stats_checks
import subprocess
from collections import namedtuple


class TestRunSamtoolsCommands(TestCase):

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
        self.assertRaises(RuntimeError, stats_checks.RunSamtoolsCommands._run_subprocess, ['samtools', 'quickcheck', 'mybam'])
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


class TestHandleSamtoolsStats(TestCase):

    def test_extract_seq_checksum_from_stats_1(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\nCHK     1bfca46a        2046405a        f4f56eb9\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = "CHK     1bfca46a        2046405a        f4f56eb9"
        actual_result = stats_checks.HandleSamtoolsStats.extract_seq_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_extract_seq_checksum_from_stats_2(self):
        stats = ""
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.extract_seq_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_extract_seq_checksum_from_stats_3(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.extract_seq_checksum_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.utils.read_from_file')
    def test_get_stats_1(self, mock_readf, mock_path):
        mock_readf.return_value = 'some stats'
        mock_path.isfile.return_value = True
        result = stats_checks.HandleSamtoolsStats._get_stats('some path')
        expected = 'some stats'
        self.assertEqual(result, expected)

    @mock.patch('checks.stats_checks.os.path')
    def test_get_stats_2(self, mock_path):
        mock_path.isfile.return_value = False
        result = stats_checks.HandleSamtoolsStats._get_stats('some path')
        expected = None
        self.assertEqual(result, expected)

    def test_get_stats_3(self):
        result = stats_checks.HandleSamtoolsStats._get_stats(None)
        expected = None
        self.assertEqual(result, expected)


    @mock.patch('checks.stats_checks.os.path')
    def test_generate_stats_1(self, mock_path):
        mock_path.isfile.return_value = False
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats._generate_stats, 'some_path')

    def test_generate_stats_2(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats._generate_stats, None)

    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_stats_output')
    def test_generate_stats_3(self, mock_stats, mock_path):
        mock_stats.return_value = 'some stats'
        mock_path.isfile.return_value = True
        result = stats_checks.HandleSamtoolsStats._generate_stats('some path')
        expected = 'some stats'
        self.assertEqual(result, expected)


    def test_persist_stats_when_empty_params(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.persist_stats, None, None)

    def test_persist_stats_when_one_empty_param(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.persist_stats, None, 'irrelevant')

    @mock.patch('checks.stats_checks.os.path')
    def test_persist_stats_when_existing_stats_file(self, mock_path):
        mock_path.isfile.return_value = True
        result = stats_checks.HandleSamtoolsStats.persist_stats('some stats', 'some path')
        self.assertFalse(result)

    @mock.patch('checks.utils.write_to_file')
    def test_persist_stats_when_ok(self, mock_writef):
        mock_writef.return_value = True
        result = stats_checks.HandleSamtoolsStats.persist_stats('some stats', 'some path')
        expected = True
        self.assertEqual(result, expected)

    @mock.patch('checks.stats_checks.utils.can_read_file')
    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats._get_stats')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats._is_stats_file_older_than_data')
    def test_fetch_stats_returns_stats(self, mock_older, mock_stats, mock_path, mock_can_read):
        mock_can_read.return_value = True
        mock_older.return_value = False
        mock_stats.return_value = 'some stats'
        mock_path.isfile.return_value = True
        result = stats_checks.HandleSamtoolsStats.fetch_stats('bam path', 'stats path')
        expected = 'some stats'
        self.assertEqual(result, expected)

    def test_fetch_stats_with_empty_params(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.fetch_stats, None, 'some path')

    def test_fetch_stats_with_invalid_params(self):
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsStats.fetch_stats, 'invalid path', 'invalid path')

    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats._generate_stats')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats._get_stats')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats._is_stats_file_older_than_data')
    def test_fetch_stats_by_generating(self, mock_older, mock_get_s, mock_gen_s, mock_path):
        mock_get_s.return_value = None
        mock_older.return_value = True
        mock_gen_s.return_value = 'some stats'
        mock_path.isfile.return_value = True
        result = stats_checks.HandleSamtoolsStats.fetch_stats('some path', 'some other path')
        expected = 'some stats'
        self.assertEqual(result, expected)

    @mock.patch('checks.stats_checks.utils.compare_mtimestamp')
    def test_is_stats_file_older_than_data_when_older(self, mock_cmpts):
        mock_cmpts.return_value = 1
        self.assertTrue(stats_checks.HandleSamtoolsStats._is_stats_file_older_than_data('some path', 'other path'))

    @mock.patch('checks.stats_checks.utils.compare_mtimestamp')
    def test_is_stats_file_older_than_data_when_not(self, mock_cmpts):
        mock_cmpts.return_value = -1
        self.assertFalse(stats_checks.HandleSamtoolsStats._is_stats_file_older_than_data('some path', 'other path'))


class TestCompareStatsForFiles(TestCase):

    def test_compare_flagstats_when_different(self):
        result = stats_checks.CompareStatsForFiles.compare_flagstats('flagstat1', 'flagstat2')
        self.assertEqual(len(result), 1)

    def test_compare_flagstats_when_equal(self):
        result = stats_checks.CompareStatsForFiles.compare_flagstats('flagstat1', 'flagstat1')
        self.assertEqual(len(result), 0)

    def test_compare_flagstats_when_empty_params(self):
        result = stats_checks.CompareStatsForFiles.compare_flagstats(None, None)
        self.assertEqual(len(result), 1)

    def test_compare_flagstats_when_one_param_empty(self):
        result = stats_checks.CompareStatsForFiles.compare_flagstats(None, 'some flagstat')
        self.assertEqual(len(result), 1)



    def test_compare_stats_by_sequence_checksum_1(self):
        result = stats_checks.CompareStatsForFiles.compare_stats_by_sequence_checksum('stats1\nCHK 1234', 'stats2\nCHK 1234')
        self.assertEqual(len(result), 0)

    def test_compare_stats_by_sequence_checksum_2(self):
        result = stats_checks.CompareStatsForFiles.compare_stats_by_sequence_checksum('stats1\nCHK 1234', 'stats2\nCHK 7777')
        self.assertEqual(len(result), 1)

    def test_compare_stats_by_sequence_checksum_3(self):
        result = stats_checks.CompareStatsForFiles.compare_stats_by_sequence_checksum('stats1\nCHK 1234', '')
        self.assertEqual(len(result), 1)

    def test_compare_stats_by_sequence_checksum_4(self):
        result = stats_checks.CompareStatsForFiles.compare_stats_by_sequence_checksum('stats1\n', 'stats2\n')
        self.assertEqual(len(result), 2)

    def test_compare_bam_and_cram_by_statistics_1(self):
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics('', '')
        self.assertEqual(len(result), 2)

    @mock.patch('checks.stats_checks.os.path')
    def test_compare_bam_and_cram_by_statistics_2(self, mock_path):
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics('', 'some path')
        mock_path.isfile.return_value = True
        self.assertEqual(len(result), 1)

    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.utils')
    def test_compare_bam_and_cram_by_statistics(self, mock_readf, mock_path):
        mock_readf.can_read_file.return_value = False
        mock_path.isfile.return_value = True
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics('bam path', 'cram path')
        self.assertEqual(len(result), 2)


    @mock.patch('checks.stats_checks.os.path')
    @mock.patch('checks.stats_checks.utils')
    @mock.patch('checks.stats_checks.RunSamtoolsCommands')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats.fetch_stats')
    @mock.patch('checks.stats_checks.HandleSamtoolsStats.persist_stats')
    def test_compare_bam_and_cram_by_statistics(self, mock_persist_stats, mock_fetch_stats, mock_samt, mock_utils, mock_path):
        mock_path.isfile.return_value = True
        mock_utils.can_read_file.return_value = True
        mock_samt.get_samtools_flagstat_output.return_value = 'flag'
        mock_fetch_stats.side_effect = ['\nCHK 123', '\nCHK 456']
        mock_persist_stats.return_value = True
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics('some bam', 'some cram')
        self.assertEqual(len(result), 1)


class TestHandleSamtoolsVersion(TestCase):

    def test_get_version_nr_from_samtools_output_1_3(self):
        samtools_output = "samtools 1.3\nUsing htslib 1.3\nCopyright (C) 2015 Genome Research Ltd.\n"
        result = stats_checks.HandleSamtoolsVersion._get_version_nr_from_samtools_output(samtools_output)
        expected = "1.3"
        self.assertEqual(result, expected)

    def test_get_version_nr_from_samtools_output_1_1(self):
        samtools_output = "samtools 1.1\nUsing htslib 1.1\nCopyright (C) 2014 Genome Research Ltd.\n"
        result = stats_checks.HandleSamtoolsVersion._get_version_nr_from_samtools_output(samtools_output)
        expected = "1.1"
        self.assertEqual(result, expected)

    def test_get_version_nr_from_samtools_output_git_1_2(self):
        samtools_output = "samtools 1.2-216-gdffc67f\nUsing htslib 1.2.1-218-g9f6fa0f\nCopyright (C) 2015 Genome Research Ltd.\n"
        result = stats_checks.HandleSamtoolsVersion._get_version_nr_from_samtools_output(samtools_output)
        expected = "1.2-216-gdffc67f"
        self.assertEqual(result, expected)

    def test_get_version_nr_from_samtools_output_git_1_218(self):
        samtools_output = "samtools 1.2-218-g00e55ad\nUsing htslib 1.2.1-218-g9f6fa0f\nCopyright (C) 2015 Genome Research Ltd.\n"
        result = stats_checks.HandleSamtoolsVersion._get_version_nr_from_samtools_output(samtools_output)
        expected = "1.2-218-g00e55ad"
        self.assertEqual(result, expected)


    def test_extract_major_version_nr_1_1(self):
        version = "1.1"
        result = stats_checks.HandleSamtoolsVersion._extract_major_version_nr(version)
        expected = "1"
        self.assertEqual(result, expected)

    def test_extract_major_version_nr_1_3(self):
        version = "1.3"
        result = stats_checks.HandleSamtoolsVersion._extract_major_version_nr(version)
        expected = "1"
        self.assertEqual(result, expected)

    def test_extract_major_version_nr_1_218(self):
        version = "1.2-218-g00e55ad"
        result = stats_checks.HandleSamtoolsVersion._extract_major_version_nr(version)
        expected = "1"
        self.assertEqual(result, expected)

    def test_extract_major_version_nr_1_218(self):
        version = "1.2-218-g00e55ad"
        result = stats_checks.HandleSamtoolsVersion._extract_major_version_nr(version)
        expected = "1"
        self.assertEqual(result, expected)

    def test_extract_major_version_nr_0_2(self):
        version = "0.2.0-rc7-68-g8b268c0"
        result = stats_checks.HandleSamtoolsVersion._extract_major_version_nr(version)
        expected = "0"
        self.assertEqual(result, expected)


    def test_extract_minor_version_nr_1_3(self):
        version = "1.3"
        result = stats_checks.HandleSamtoolsVersion._extract_minor_version_nr(version)
        expected = "3"
        self.assertEqual(result, expected)

    def test_extract_minor_version_nr_1_218(self):
        version = "1.2-218-g00e55ad"
        result = stats_checks.HandleSamtoolsVersion._extract_minor_version_nr(version)
        expected = "2"
        self.assertEqual(result, expected)

    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_version_output')
    def test_check_samtools_version_wrong_vs_1_2(self, mock_version):
        mock_version.return_value = 'samtools 1.2\nUsing htslib 1.2.1\nCopyright (C) 2015 Genome Research Ltd.'
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsVersion.check_samtools_version, mock_version)

    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_version_output')
    def test_check_samtools_version_wrong_vs_1_218(self, mock_version):
        mock_version.return_value = "samtools 1.2-218-g00e55ad\nUsing htslib 1.2.1-218-g9f6fa0f\nCopyright (C) 2015 Genome Research Ltd.\n"
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsVersion.check_samtools_version, mock_version)

    @mock.patch('checks.stats_checks.RunSamtoolsCommands.get_samtools_version_output')
    def test_check_samtools_version_no_vs(self, mock_version):
        mock_version.return_value = None
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsVersion.check_samtools_version, mock_version)

    def test_check_samtools_version_ok_vs(self):
        vs = "samtools 1.3\nUsing htslib 1.3\nCopyright (C) 2015 Genome Research Ltd.\n"
        result = stats_checks.HandleSamtoolsVersion.check_samtools_version(vs)
        self.assertIsNone(result)

    def test_check_samtools_version_is_random(self):
        vs = "some stuff"
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsVersion.check_samtools_version, vs)

    def test_check_samtools_version_minor_vs_is_random(self):
        vs = "1.some stuff"
        self.assertRaises(ValueError, stats_checks.HandleSamtoolsVersion.check_samtools_version, vs)



class TestUsingActualFiles(TestCase):
    def setUp(self):
        self.test_data_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-cases')

    def test_compare_bam_and_cram_equivalent_files(self):
        bam_path = os.path.join(self.test_data_dirpath, 'ok_bam_cram/mpileup.3.bam')
        cram_path = os.path.join(self.test_data_dirpath, 'ok_bam_cram/mpileup.3.cram')
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics(bam_path, cram_path)
        self.assertEqual(len(result), 0)

    def test_compare_bam_and_cram_fail_quickcheck(self):
        """
        I've given it here 2 BAMs instead of a BAM and a CRAM because samtools 1.3 doesn't support quickcheck for crams.
        TODO: update the test when a new version of samtools is available.
        """
        bam_path = os.path.join(self.test_data_dirpath, 'fail_quickcheck/c1#ID.bam')
        cram_path = os.path.join(self.test_data_dirpath, 'fail_quickcheck/c1#clip.bam')
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics(bam_path, cram_path)
        self.assertEqual(len(result), 2)

    def test_compare_bam_and_cram_diff_stats(self):
        bam_path = os.path.join(self.test_data_dirpath, 'diff_stats/mpileup.1.bam')
        cram_path = os.path.join(self.test_data_dirpath, 'diff_stats/mpileup.3.cram')
        result = stats_checks.CompareStatsForFiles.compare_bam_and_cram_by_statistics(bam_path, cram_path)
        print("Results %s " % result)
        self.assertEqual(len(result), 2)

    



   # @mock.patch('checks.utils.can_read_file')
   #  @mock.patch('checks.utils.os.path')
   #  def test_compare_mtimestamp_when_unequal_ts_2(self, mock_path, mock_can_read):
   #      mock_can_read.return_value = True
   #      mock_path.isfile.return_value = True
   #      mock_path.getmtime.side_effect = [5, 4]
   #      result = utils.compare_mtimestamp('fpath1', 'fpath2')
   #      expected = 1
   #      self.assertEqual(result, expected)




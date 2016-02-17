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

from checks import utils

@mock.patch('checks.utils.os.path')
@mock.patch('checks.utils.os.access')
class TestCheckPathWritable(unittest.TestCase):

    def test_check_path_writable_1(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = False
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    def test_check_path_writable_2(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = False
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))

    def test_check_path_writable_3(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = True
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    def test_check_path_writable_4(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = True
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))

    def test_check_path_writable_5(self, mock_access, mock_path):
        mock_path.isdir.return_value = True
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    def test_check_path_writable_6(self, mock_access, mock_path):
        mock_path.isdir.return_value = True
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))


class TestReadWriteDisk(unittest.TestCase):

    @mock.patch('checks.utils.open')
    def test_read_from_file(self, mock_open):
        utils.read_from_file('blah')
        mock_open.assert_called_once_with('blah')

    def test_write_from_file(self):
        with mock.patch('checks.utils.open') as mock_open:
            utils.write_to_file('blah', 'some_text')
            mock_open.assert_called_once_with('blah', 'w')

    def test_logging_1(self):
        with mock.patch('checks.utils.logging.info') as mock_logging:
            utils.log_error('samtools quickcheck', None, 0)
            mock_logging.assert_called_once_with('Ran successfully samtools quickcheck')

    def test_logging_2(self):
        with mock.patch('checks.utils.logging.error') as mock_logging:
            utils.log_error('samtools quickcheck', None, 1)
            mock_logging.assert_called_once_with('samtools quickcheck had no error, but exit code is non zero: 1')

    def test_logging_3(self):
        with mock.patch('checks.utils.logging.error') as mock_logging:
            utils.log_error('samtools quickcheck', "error", 1)
            mock_logging.assert_called_once_with('samtools quickcheck exited with code: 1 and threw an error: error ')

    def test_logging_4(self):
        with mock.patch('checks.utils.logging.error') as mock_logging:
            utils.log_error('samtools quickcheck', "error", 0)
            mock_logging.assert_called_once_with('samtools quickcheck had exit status 0, but threw an error: error ')



class TestCompareTimestamps(unittest.TestCase):

    def test_compare_mtimestamp_when_empty_params(self):
        self.assertRaises(ValueError, utils.compare_mtimestamp, None, None)

    def test_compare_mtimestamp_when_one_param_empty(self):
        self.assertRaises(ValueError, utils.compare_mtimestamp, None, 'some path')

    def test_compare_mtimestamp_when_nonexisting_path1(self):
        self.assertRaises(IOError, utils.compare_mtimestamp, 'nonexisting path', 'irrelevant')

    def test_compare_mtimestamp_when_nonexisting_path2(self):
        self.assertRaises(IOError, utils.compare_mtimestamp, 'irrelevant', 'nonexisting path2')


    @mock.patch('checks.utils.can_read_file')
    @mock.patch('checks.utils.os.path')
    def test_compare_mtimestamp_when_unequal_ts_1(self, mock_path, mock_can_read):
        mock_can_read.return_value = True
        mock_path.isfile.return_value = True
        mock_path.getmtime.side_effect = [4, 5]
        result = utils.compare_mtimestamp('fpath1', 'fpath2')
        expected = -1
        self.assertEqual(result, expected)

    @mock.patch('checks.utils.can_read_file')
    @mock.patch('checks.utils.os.path')
    def test_compare_mtimestamp_when_unequal_ts_2(self, mock_path, mock_can_read):
        mock_can_read.return_value = True
        mock_path.isfile.return_value = True
        mock_path.getmtime.side_effect = [5, 4]
        result = utils.compare_mtimestamp('fpath1', 'fpath2')
        expected = 1
        self.assertEqual(result, expected)

    @mock.patch('checks.utils.can_read_file')
    @mock.patch('checks.utils.os.path')
    def test_compare_mtimestamp_when_equal_ts(self, mock_path, mock_can_read):
        mock_can_read.return_value = True
        mock_path.isfile.return_value = True
        mock_path.getmtime.return_value = 4
        result = utils.compare_mtimestamp('fpath1', 'fpath2')
        expected = 0
        self.assertEqual(result, expected)


















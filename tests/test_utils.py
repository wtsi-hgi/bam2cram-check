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


class TestCheckPathWritable(unittest.TestCase):

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_1(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = False
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_2(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = False
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_3(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = True
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_4(self, mock_access, mock_path):
        mock_path.isdir.return_value = False
        mock_path.exists.return_value = True
        mock_path.dirname.return_value = 'some_dir'
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_5(self, mock_access, mock_path):
        mock_path.isdir.return_value = True
        mock_access.return_value = False
        self.assertFalse(utils.check_path_writable('some_path'))

    @mock.patch('utils.os.path')
    @mock.patch('stats_checks.os.access')
    def test_check_path_writable_6(self, mock_access, mock_path):
        mock_path.isdir.return_value = True
        mock_access.return_value = True
        self.assertTrue(utils.check_path_writable('some_path'))

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

from checks import stats_checks


class TestHandleSamtoolsStats(unittest.TestCase):


    def test_get_chk_from_stats_1(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\nCHK     1bfca46a        2046405a        f4f56eb9\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = "CHK     1bfca46a        2046405a        f4f56eb9"
        actual_result = stats_checks.HandleSamtoolsStats.get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_2(self):
        stats = ""
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)

    def test_get_chk_from_stats_3(self):
        stats = "# CHK, Checksum [2]Read Names   [3]Sequences    [4]Qualities\n# CHK, CRC32 of reads which passed " \
                "filtering followed by addition (32bit overflow)\n# " \
                "Summary Numbers. Use `grep ^SN | cut -f 2-` to extract this part.\nSN      raw total sequences:    " \
                "268395942"
        wanted_result = None
        actual_result = stats_checks.HandleSamtoolsStats.get_chk_from_stats(stats)
        self.assertEqual(wanted_result, actual_result)


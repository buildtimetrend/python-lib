# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Settings
#
# Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtime-trend
# <https://github.com/ruleant/buildtime-trend/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildtimetrend.settings import Settings
import buildtimetrend
import os
import unittest


class TestTools(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

        project_name = "None"
        if 'TRAVIS' in os.environ and os.getenv('TRAVIS'):
            project_name = os.getenv('TRAVIS_REPO_SLUG')

        self.project_info = {
            "version": buildtimetrend.VERSION,
            "schema_version": buildtimetrend.SCHEMA_VERSION,
            "project_name": project_name}

    def test_get_project_info(self):
        self.assertDictEqual(self.project_info, self.settings.get_project_info())

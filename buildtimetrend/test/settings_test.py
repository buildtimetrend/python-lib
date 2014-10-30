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
from buildtimetrend.collection import Collection
from buildtimetrend.keenio import keen_io_writable
from buildtimetrend.keenio import keen_io_readable
import buildtimetrend
import os
import unittest
import constants


class TestTools(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.settings = Settings()

        self.project_name = buildtimetrend.NAME

        self.project_info = {
            "version": buildtimetrend.VERSION,
            "schema_version": buildtimetrend.SCHEMA_VERSION,
            "project_name": self.project_name}

    def setUp(self):
        # reinit settings singleton
        if self.settings is not None:
            self.settings.__init__()

    def test_get_project_info(self):
        self.assertDictEqual(self.project_info, self.settings.get_project_info())

    def test_get_set_project_name(self):
        self.assertEquals(self.project_name, self.settings.get_project_name())

        self.settings.set_project_name("test_name")
        self.assertEquals("test_name", self.settings.get_project_name())

        self.settings.set_project_name(None)
        self.assertEquals(None, self.settings.get_project_name())

        self.settings.set_project_name("")
        self.assertEquals("", self.settings.get_project_name())

    def test_get_add_setting(self):
        # setting is not set yet
        self.assertEquals(None, self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", "test_value")
        self.assertEquals("test_value", self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", None)
        self.assertEquals(None, self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", "")
        self.assertEquals("", self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", 6)
        self.assertEquals(6, self.settings.get_setting("test_name"))

    def test_get_setting(self):
        self.assertEquals(None, self.settings.get_setting("test_name"))

        self.assertEquals(
            self.project_name,
            self.settings.get_setting("project_name"))

        self.assertDictEqual(
            {"project_name": self.project_name},
            self.settings.settings.get_items())

    def test_no_config_file(self):
        # function should return false when file doesn't exist
        self.assertFalse(self.settings.load_config_file('no_file.yml'))
        self.assertDictEqual(
            {"project_name": self.project_name},
            self.settings.settings.get_items())

        self.assertFalse(self.settings.load_config_file(''))
        self.assertDictEqual(
            {"project_name": self.project_name},
            self.settings.settings.get_items())

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.settings.load_config_file)

    def test_load_config_file(self):
        # checking if Keen.io configuration is not set (yet)
        self.assertFalse(keen_io_readable())
        self.assertFalse(keen_io_writable())

        # load sample config file
        self.assertTrue(self.settings.load_config_file(constants.TEST_SAMPLE_CONFIG_FILE))
        self.assertDictEqual(
            {"project_name": "test_project",
             "setting1": "test_value1"},
            self.settings.settings.get_items())

        # checking if Keen.io configuration is set
        self.assertTrue(keen_io_readable())
        self.assertTrue(keen_io_writable())

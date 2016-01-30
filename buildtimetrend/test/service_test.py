# vim: set expandtab sw=4 ts=4:
"""
Unit tests for service related functions

Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/service
<https://github.com/buildtimetrend/service/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from buildtimetrend import service
from buildtimetrend.service import format_duration
from buildtimetrend.service import check_process_parameters
from buildtimetrend.service import validate_travis_request
from buildtimetrend.service import validate_task_parameters
from buildtimetrend.settings import Settings
import unittest
import mock
import keen


class TestService(unittest.TestCase):

    """Unit tests for service related functions"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        cls.settings = Settings()

    def setUp(self):
        """Initialise test environment before each test."""
        # reinit settings singleton
        if self.settings is not None:
            self.settings.__init__()

        # reset Keen.io settings
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

    def test_is_repo_allowed(self):
        """Test is_repo_allowed()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, service.is_repo_allowed)

        # error is thrown when called with an invalid parameter
        self.assertFalse(service.is_repo_allowed(None))

        # repo is allowed by default
        self.assertTrue(service.is_repo_allowed("name/repo"))

    def test_is_repo_allowed_set_denied(self):
        """Test is_repo_allowed() by using the 'denied_repo' setting"""
        # test denied repo
        self.settings.add_setting("denied_repo", {"test1"})

        self.assertTrue(service.is_repo_allowed("name/repo"))
        self.assertFalse(service.is_repo_allowed("name/test1"))
        self.assertTrue(service.is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_denied_multi(self):
        """Test is_repo_allowed() by using multiple 'denied_repo' settings"""
        # test multiple denied repos
        self.settings.add_setting("denied_repo", {"test1", "test2"})

        self.assertTrue(service.is_repo_allowed("name/repo"))
        self.assertFalse(service.is_repo_allowed("name/test1"))
        self.assertFalse(service.is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_allowed(self):
        """Test is_repo_allowed() by using the 'allowed_repo' setting"""
        # test allowed repo
        self.settings.add_setting("allowed_repo", {"test1"})

        self.assertFalse(service.is_repo_allowed("name/repo"))
        self.assertTrue(service.is_repo_allowed("name/test1"))
        self.assertFalse(service.is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_allowed_multi(self):
        """Test is_repo_allowed() by using multiple 'allowed_repo' settings"""
        # test multiple allowed repos
        self.settings.add_setting("allowed_repo", {"test1", "test2"})

        self.assertFalse(service.is_repo_allowed("name/repo"))
        self.assertTrue(service.is_repo_allowed("name/test1"))
        self.assertTrue(service.is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_denied_allowed(self):
        """
        Test is_repo_allowed() by using both
        'allowed_repo' and 'denied_repo' settings
        """
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        # set allowed repo
        self.settings.add_setting("allowed_repo", {"name"})

        self.assertTrue(service.is_repo_allowed("name/repo"))
        self.assertFalse(service.is_repo_allowed("name/test1"))
        self.assertTrue(service.is_repo_allowed("name/test2"))
        self.assertFalse(service.is_repo_allowed("owner/repo"))

    def test_get_repo_data_detail(self):
        """Test get_repo_data_detail()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, service.get_repo_data_detail)

        # default global setting 'data_detail' is returned when no repo matches
        self.assertEqual("full", service.get_repo_data_detail(None))
        self.assertEqual("full", service.get_repo_data_detail(""))
        self.assertEqual("full", service.get_repo_data_detail("test/repo"))

        # set other default 'data_detail' setting
        self.settings.add_setting("data_detail", "minimal")
        self.assertEqual("minimal", service.get_repo_data_detail(None))
        self.assertEqual("minimal", service.get_repo_data_detail(""))
        self.assertEqual("minimal", service.get_repo_data_detail("test/repo"))

        # set repo settings
        self.settings.add_setting(
            "repo_data_detail",
            {
                "user1/": "basic",
                "user2/test_repo_full": "full",
                "test_repo_ext": "extended"
            }
        )
        self.assertEqual("minimal", service.get_repo_data_detail(""))
        self.assertEqual("minimal", service.get_repo_data_detail("test/repo"))
        self.assertEqual("basic", service.get_repo_data_detail("user1/repo1"))
        self.assertEqual("basic", service.get_repo_data_detail("user1/repo2"))
        self.assertEqual(
            "minimal",
            service.get_repo_data_detail("user2/repo2")
        )
        self.assertEqual(
            "full",
            service.get_repo_data_detail("user2/test_repo_full")
        )
        # test matching substring
        # don't test "user1/test_repo_ext", result could match two rules
        self.assertEqual(
            "extended",
            service.get_repo_data_detail("user2/test_repo_ext")
        )
        self.assertEqual(
            "extended",
            service.get_repo_data_detail("user3/test_repo_ext")
        )

    def test_format_duration(self):
        """Test format_duration()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, format_duration)

        self.assertEqual("unknown", format_duration(None))
        self.assertEqual("unknown", format_duration("string"))
        self.assertEqual("unknown", format_duration(-1))

        self.assertEqual("0s", format_duration(0))
        self.assertEqual("1s", format_duration(1))
        self.assertEqual("1s", format_duration(1.4))
        self.assertEqual("2s", format_duration(1.9))
        self.assertEqual("2s", format_duration(2.1))

        self.assertEqual("59s", format_duration(59.1))
        self.assertEqual("1m 0s", format_duration(59.7))
        self.assertEqual("1m 0s", format_duration(60))
        self.assertEqual("1m 0s", format_duration(60.3))
        self.assertEqual("1m 1s", format_duration(60.6))
        self.assertEqual("1m 1s", format_duration(61))

        self.assertEqual("59m 59s", format_duration(3599.3))
        self.assertEqual("1h 0m 0s", format_duration(3599.7))
        self.assertEqual("1h 0m 0s", format_duration(3600))
        self.assertEqual("1h 0m 0s", format_duration(3600.3))
        self.assertEqual("1h 0m 1s", format_duration(3601))

        self.assertEqual("2h 5m 0s", format_duration(7500))

    def test_check_process_parameters(self):
        """Test check_process_parameters()"""
        # repo or build is not set
        no_repo_build = "Repo or build are not set, format : " \
            "/travis/<repo_owner>/<repo_name>/<build>"

        self.assertEqual(no_repo_build, check_process_parameters())
        self.assertEqual(no_repo_build, check_process_parameters("user/repo"))
        self.assertEqual(no_repo_build, check_process_parameters(None, 1234))

        # repo is not allowed
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        self.assertEqual(
            "Project 'user/test1' is not allowed.",
            check_process_parameters("user/test1", 1234)
        )

        # Keen.io write key is not set
        self.assertEqual(
            "Keen IO write key not set, no data was sent",
            check_process_parameters("user/repo", 1234)
        )

        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"
        with self.assertRaises(Exception) as exc:
            check_process_parameters("user/repo", 1234)
        self.assertEqual(
            "Error checking if build exists.", str(exc.exception)
        )

    @mock.patch('buildtimetrend.service.has_build_id', return_value=True)
    def test_check_process_parameters_mock(self, has_build_id_func):
        """Test check_process_parameters() mocking has_build_id()"""
        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"

        self.assertEqual(
            "Build #1234 of project user/repo already exists in database",
            check_process_parameters("user/repo", 1234)
        )

        has_build_id_func.return_value = False
        self.assertEqual(None, check_process_parameters("user/repo", 1234))

    def test_validate_travis_request(self):
        """Test validate_travis_request()"""
        # repo or build is not set
        no_repo_build = "Repo or build are not set, format : " \
            "/travis/<repo_owner>/<repo_name>/<build>"

        self.assertEqual(no_repo_build, validate_travis_request())
        self.assertEqual(no_repo_build, validate_travis_request("user/repo"))
        self.assertEqual(no_repo_build, validate_travis_request(None, 1234))

        # repo is not allowed
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        self.assertEqual(
            "Project 'user/test1' is not allowed.",
            validate_travis_request("user/test1", 1234)
        )

    def test_validate_task_parameters(self):
        """Test validate_task_parameters()"""
        # Keen.io write key is not set
        self.assertEqual(
            "Keen IO write key not set, no data was sent",
            validate_task_parameters("user/repo", 1234)
        )

        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"
        with self.assertRaises(Exception) as exc:
            validate_task_parameters("user/repo", 1234)
        self.assertEqual(
            "Error checking if build exists.", str(exc.exception)
        )

    @mock.patch('buildtimetrend.service.has_build_id', return_value=True)
    def test_validate_task_parameters_mock(self, has_build_id_func):
        """Test validate_task_parameters() mocking has_build_id()"""
        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"

        self.assertEqual(
            "Build #1234 of project user/repo already exists in database",
            validate_task_parameters("user/repo", 1234)
        )

        has_build_id_func.return_value = False
        self.assertEqual(None, validate_task_parameters("user/repo", 1234))

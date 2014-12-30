# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Trend class
#
# Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtimetrend/python-lib
# <https://github.com/buildtimetrend/python-lib/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import buildtimetrend
from buildtimetrend.settings import Settings
from buildtimetrend.build import Build
from buildtimetrend.stages import Stage
from buildtimetrend.stages import Stages
import constants
from lxml import etree
import unittest


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.build = Build()
        # show full diff in case of assert mismatch
        self.maxDiff = None

    def test_novalue(self):
        # number of stages should be zero
        self.assertEquals(0, len(self.build.stages.stages))
        self.assertEquals(0, self.build.properties.get_size())

        # get properties should return zero duration
        self.assertDictEqual({'duration': 0}, self.build.get_properties())

        # dict should be empty
        self.assertDictEqual(
            {'duration': 0, 'stages': []},
            self.build.to_dict()
        )

        # list should be empty
        self.assertListEqual([], self.build.stages_to_list())

        # xml shouldn't contain items
        self.assertEquals(
            '<build><stages/></build>', etree.tostring(self.build.to_xml()))
        self.assertEquals(
            '<build>\n'
            '  <stages/>\n'
            '</build>\n', self.build.to_xml_string())

    def test_nofile(self):
        # number of stages should be zero when file doesn't exist
        self.build = Build('nofile.csv')
        self.assertEquals(0, len(self.build.stages.stages))

        self.build = Build('')
        self.assertEquals(0, len(self.build.stages.stages))

    def test_end_timestamp(self):
        self.assertEquals(0, self.build.stages.end_timestamp)

        self.build = Build('', 123)
        self.assertEquals(123, self.build.stages.end_timestamp)

    def test_add_stages(self):
        self.build.add_stages(None)
        self.assertEquals(0, len(self.build.stages.stages))

        self.build.add_stages("string")
        self.assertEquals(0, len(self.build.stages.stages))

        stages = Stages()
        stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)
        self.build.add_stages(stages)
        self.assertEquals(3, len(self.build.stages.stages))

        # stages should not change when submitting an invalid object
        self.build.add_stages(None)
        self.assertEquals(3, len(self.build.stages.stages))

        self.build.add_stages("string")
        self.assertEquals(3, len(self.build.stages.stages))

        self.build.add_stages(Stages())
        self.assertEquals(0, len(self.build.stages.stages))

    def test_add_stage(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.build.add_stage)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.build.add_stage, None)
        self.assertRaises(TypeError, self.build.add_stage, "string")

        # add a stage
        stage = Stage()
        stage.set_name("stage1")
        stage.set_started_at(constants.TIMESTAMP_STARTED)
        stage.set_finished_at(constants.TIMESTAMP1)
        stage.set_duration(235)

        self.build.add_stage(stage)

        # test number of stages
        self.assertEquals(1, len(self.build.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.build.stages.started_at
        )

        # test finished_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP1,
            self.build.stages.finished_at
        )

        # test stages (names + duration)
        self.assertListEqual(
           [{'duration': 235,
             'finished_at': constants.SPLIT_TIMESTAMP1,
             'name': 'stage1',
             'started_at': constants.SPLIT_TIMESTAMP_STARTED}],
            self.build.stages.stages)

        # add another stage
        stage = Stage()
        stage.set_name("stage2")
        stage.set_started_at(constants.TIMESTAMP1)
        stage.set_finished_at(constants.TIMESTAMP_FINISHED)
        stage.set_duration(136.234)

        self.build.add_stage(stage)

        # test number of stages
        self.assertEquals(2, len(self.build.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.build.stages.started_at
        )

        # test finished_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_FINISHED,
            self.build.stages.finished_at
        )

        # test stages (names + duration)
        self.assertListEqual(
           [{'duration': 235,
             'finished_at': constants.SPLIT_TIMESTAMP1,
             'name': 'stage1',
             'started_at': constants.SPLIT_TIMESTAMP_STARTED},
            {'duration': 136.234,
             'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
             'name': 'stage2',
             'started_at': constants.SPLIT_TIMESTAMP1}],
            self.build.stages.stages)

    def test_add_property(self):
        self.build.add_property('property1', 2)
        self.assertEquals(1, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2},
            self.build.properties.get_items()
        )

        self.build.add_property('property2', 3)
        self.assertEquals(2, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2, 'property2': 3},
            self.build.properties.get_items()
        )

        self.build.add_property('property2', 4)
        self.assertEquals(2, self.build.properties.get_size())
        self.assertDictEqual(
            {'property1': 2, 'property2': 4},
            self.build.properties.get_items()
        )

    def test_get_property(self):
        self.build.add_property('property1', 2)
        self.assertEquals(2, self.build.get_property('property1'))

        self.build.add_property('property1', None)
        self.assertEquals(None, self.build.get_property('property1'))

        self.build.add_property('property2', 3)
        self.assertEquals(3, self.build.get_property('property2'))

        self.build.add_property('property2', 4)
        self.assertEquals(4, self.build.get_property('property2'))

    def test_get_property_does_not_exist(self):
        self.assertEquals(None, self.build.get_property('no_property'))

    def test_get_properties(self):
        self.build.add_property('property1', 2)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2},
            self.build.get_properties())

        self.build.add_property('property2', 3)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2, 'property2': 3},
            self.build.get_properties())

        self.build.add_property('property2', 4)
        self.assertDictEqual(
            {'duration': 0, 'property1': 2, 'property2': 4},
            self.build.get_properties())

    def test_load_properties(self):
        self.build.load_properties_from_settings()

        self.assertDictEqual(
            {'duration': 0, "repo": buildtimetrend.NAME},
            self.build.get_properties())

        settings = Settings()
        settings.add_setting("ci_platform", "travis")
        settings.add_setting("build", "123")
        settings.add_setting("job", "123.1")
        settings.add_setting("branch", "branch1")
        settings.add_setting("result", "passed")
        settings.set_project_name("test/project")

        self.build.load_properties_from_settings()
        self.assertDictEqual(
            {'duration': 0,
             'ci_platform': "travis",
             'build': "123",
             'job': "123.1",
             'branch': "branch1",
             'result': "passed",
             'repo': "test/project"},
            self.build.get_properties())

    def test_to_dict(self):
        # read and parse sample file
        self.build = Build(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test dict
        self.assertDictEqual(
            {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4,
            'stages':
            [{'duration': 2,
              'finished_at': constants.SPLIT_TIMESTAMP2,
              'name': 'stage1',
              'started_at': constants.SPLIT_TIMESTAMP1},
             {'duration': 5,
              'finished_at': constants.SPLIT_TIMESTAMP3,
              'name': 'stage2',
              'started_at': constants.SPLIT_TIMESTAMP2},
             {'duration': 10,
              'finished_at': constants.SPLIT_TIMESTAMP4,
              'name': 'stage3',
              'started_at': constants.SPLIT_TIMESTAMP3}]
            },
            self.build.to_dict())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # started_at property should override default value
        self.build.set_started_at(constants.ISOTIMESTAMP_STARTED)
        # finished_at property should override default value
        self.build.set_finished_at(constants.ISOTIMESTAMP_FINISHED)
        # test dict
        self.assertDictEqual(
            {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP_STARTED,
            'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
            'property1': 2, 'property2': 3,
            'stages':
            [{'duration': 2,
              'finished_at': constants.SPLIT_TIMESTAMP2,
              'name': 'stage1',
              'started_at': constants.SPLIT_TIMESTAMP1},
             {'duration': 5,
              'finished_at': constants.SPLIT_TIMESTAMP3,
              'name': 'stage2',
              'started_at': constants.SPLIT_TIMESTAMP2},
             {'duration': 10,
              'finished_at': constants.SPLIT_TIMESTAMP4,
              'name': 'stage3',
              'started_at': constants.SPLIT_TIMESTAMP3}]
            },
            self.build.to_dict())

    def test_stages_to_list(self):
        # read and parse sample file
        self.build = Build(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test list
        self.assertListEqual(
            [{'stage': {'duration': 2,
              'finished_at': constants.SPLIT_TIMESTAMP2,
              'name': 'stage1',
              'started_at': constants.SPLIT_TIMESTAMP1},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4}},
            {'stage': {'duration': 5,
              'finished_at': constants.SPLIT_TIMESTAMP3,
              'name': 'stage2',
              'started_at': constants.SPLIT_TIMESTAMP2},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4}},
            {'stage': {'duration': 10,
              'finished_at': constants.SPLIT_TIMESTAMP4,
              'name': 'stage3',
              'started_at': constants.SPLIT_TIMESTAMP3},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP1,
            'finished_at': constants.SPLIT_TIMESTAMP4}},
            ],
            self.build.stages_to_list())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # started_at property should override default value
        self.build.set_started_at(constants.ISOTIMESTAMP_STARTED)
        # finished_at property should override default value
        self.build.set_finished_at(constants.ISOTIMESTAMP_FINISHED)
        # test dict
        self.assertListEqual(
            [{'stage': {'duration': 2,
              'finished_at': constants.SPLIT_TIMESTAMP2,
              'name': 'stage1',
              'started_at': constants.SPLIT_TIMESTAMP1},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP_STARTED,
            'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
            'property1': 2, 'property2': 3}},
            {'stage': {'duration': 5,
              'finished_at': constants.SPLIT_TIMESTAMP3,
              'name': 'stage2',
              'started_at': constants.SPLIT_TIMESTAMP2},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP_STARTED,
            'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
            'property1': 2, 'property2': 3}},
            {'stage': {'duration': 10,
              'finished_at': constants.SPLIT_TIMESTAMP4,
              'name': 'stage3',
              'started_at': constants.SPLIT_TIMESTAMP3},
            'build': {'duration': 17,
            'started_at': constants.SPLIT_TIMESTAMP_STARTED,
            'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
            'property1': 2, 'property2': 3}},
            ],
            self.build.stages_to_list())

    def test_to_xml(self):
        # read and parse sample file
        self.build = Build(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml output
        self.assertEquals(
            '<build><stages><stage duration="2.0" name="stage1"/>'
            '<stage duration="5.0" name="stage2"/>'
            '<stage duration="10.0" name="stage3"/></stages></build>',
            etree.tostring(self.build.to_xml()))

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # test xml output
        self.assertEquals(
            '<build property1="2" property2="3">'
            '<stages><stage duration="2.0" name="stage1"/>'
            '<stage duration="5.0" name="stage2"/>'
            '<stage duration="10.0" name="stage3"/></stages></build>',
            etree.tostring(self.build.to_xml()))

    def test_to_xml_string(self):
        # read and parse sample file
        self.build = Build(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml string output
        self.assertEquals(
            '<build>\n'
            '  <stages>\n'
            '    <stage duration="2.0" name="stage1"/>\n'
            '    <stage duration="5.0" name="stage2"/>\n'
            '    <stage duration="10.0" name="stage3"/>\n'
            '  </stages>\n'
            '</build>\n',
            self.build.to_xml_string())

        # add properties
        self.build.add_property('property1', 2)
        self.build.add_property('property2', 3)
        # test xml string output
        self.assertEquals(
            '<build property1="2" property2="3">\n'
            '  <stages>\n'
            '    <stage duration="2.0" name="stage1"/>\n'
            '    <stage duration="5.0" name="stage2"/>\n'
            '    <stage duration="10.0" name="stage3"/>\n'
            '  </stages>\n'
            '</build>\n',
            self.build.to_xml_string())

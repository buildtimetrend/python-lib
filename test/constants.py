# vim: set expandtab sw=4 ts=4:
#
# Constants used by several unit tests
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

TEST_SAMPLE_FILE = 'test/testsample_timestamps.csv'
SPLIT_TIMESTAMP1 = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '58',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '55',
    'timestamp': '2014-04-01T18:58:55',
    'year': '2014'}
SPLIT_TIMESTAMP2 = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '58',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '57',
    'timestamp': '2014-04-01T18:58:57',
    'year': '2014'}
SPLIT_TIMESTAMP3 = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '59',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '02',
    'timestamp': '2014-04-01T18:59:02',
    'year': '2014'}
SPLIT_TIMESTAMP4 = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '59',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '12',
    'timestamp': '2014-04-01T18:59:12',
    'year': '2014'}
SPLIT_TIMESTAMP_ENDTAG = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '59',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '15',
    'timestamp': '2014-04-01T18:59:15',
    'year': '2014'}
STAGES_RESULT = [{'duration': 17,
             'finished_at': SPLIT_TIMESTAMP4,
             'name': 'stage1',
             'started_at': SPLIT_TIMESTAMP1}]

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

TEST_SAMPLE_TIMESTAMP_FILE = 'test/testsample_timestamps.csv'
TEST_SAMPLE_CONFIG_FILE = 'test/testsample_config.yml'

TIMESTAMP_SPLIT_EPOCH = {
    "isotimestamp": "1970-01-01T00:00:00+00:00",
    "timestamp_seconds": 0.0,
    "year": "1970",
    "month": "01",
    "month_short_en": "Jan",
    "month_full_en": "January",
    "day_of_month": "01",
    "day_of_week": "4",
    "day_of_week_short_en": "Thu",
    "day_of_week_full_en": "Thursday",
    "hour_12": "12",
    "hour_ampm": "AM",
    "hour_24": "00",
    "minute": "00",
    "second": "00",
    "microsecond": "000000",
    "timezone": "UTC",
    "timezone_offset": "+0000"
}

TIMESTAMP_SPLIT_EPOCH_NOTZ = {
    "isotimestamp": "1970-01-01T00:00:00",
    "timestamp_seconds": 0.0,
    "year": "1970",
    "month": "01",
    "month_short_en": "Jan",
    "month_full_en": "January",
    "day_of_month": "01",
    "day_of_week": "4",
    "day_of_week_short_en": "Thu",
    "day_of_week_full_en": "Thursday",
    "hour_12": "12",
    "hour_ampm": "AM",
    "hour_24": "00",
    "minute": "00",
    "second": "00",
    "microsecond": "000000",
    "timezone": "",
    "timezone_offset": ""
}

TIMESTAMP_TESTDATE = 1404913113.456789
TIMESTAMP_NANO_TESTDATE = 1404913113456789000
ISOTIMESTAMP_TESTDATE = "2014-07-09T13:38:33.456789Z"
TIMESTAMP_SPLIT_TESTDATE = {
    "isotimestamp": "2014-07-09T13:38:33.456789+00:00",
    "timestamp_seconds": TIMESTAMP_TESTDATE,
    "year": "2014",
    "month": "07",
    "month_short_en": "Jul",
    "month_full_en": "July",
    "day_of_month": "09",
    "day_of_week": "3",
    "day_of_week_short_en": "Wed",
    "day_of_week_full_en": "Wednesday",
    "hour_12": "01",
    "hour_ampm": "PM",
    "hour_24": "13",
    "minute": "38",
    "second": "33",
    "microsecond": "456789",
    "timezone": "UTC",
    "timezone_offset": "+0000"
}

TIMESTAMP_STARTED = 1396378500
TIMESTAMP_NANO_STARTED = 1396378500000000000
ISOTIMESTAMP_STARTED = '2014-04-01T18:55:00+00:00'
SPLIT_TIMESTAMP_STARTED = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '06',
    'hour_24': '18',
    'hour_ampm': 'PM',
    'minute': '55',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '00',
    'microsecond': '000000',
    'isotimestamp': ISOTIMESTAMP_STARTED,
    'timestamp_seconds': 1396378500.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}

TIMESTAMP1 = 1396378735
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
    'microsecond': '000000',
    'isotimestamp': '2014-04-01T18:58:55+00:00',
    'timestamp_seconds': 1396378735.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}
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
    'microsecond': '000000',
    'isotimestamp': '2014-04-01T18:58:57+00:00',
    'timestamp_seconds': 1396378737.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}
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
    'microsecond': '000000',
    'isotimestamp': '2014-04-01T18:59:02+00:00',
    'timestamp_seconds': 1396378742.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}
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
    'microsecond': '000000',
    'isotimestamp': '2014-04-01T18:59:12+00:00',
    'timestamp_seconds': 1396378752.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}
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
    'microsecond': '000000',
    'isotimestamp': '2014-04-01T18:59:15+00:00',
    'timestamp_seconds': 1396378755.0,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}

TIMESTAMP_FINISHED = 1396378871.234
TIMESTAMP_NANO_FINISHED = 1396378871234000000
ISOTIMESTAMP_FINISHED = '2014-04-01T19:01:11.234000+00:00'
SPLIT_TIMESTAMP_FINISHED = {'day_of_month': '01',
    'day_of_week': '2',
    'day_of_week_full_en': 'Tuesday',
    'day_of_week_short_en': 'Tue',
    'hour_12': '07',
    'hour_24': '19',
    'hour_ampm': 'PM',
    'minute': '01',
    'month': '04',
    'month_full_en': 'April',
    'month_short_en': 'Apr',
    'second': '11',
    'microsecond': '234000',
    'isotimestamp': '2014-04-01T19:01:11.234000+00:00',
    'timestamp_seconds': TIMESTAMP_FINISHED,
    'year': '2014',
    'timezone': 'UTC',
    'timezone_offset': '+0000'
}
STAGES_RESULT = [{'duration': 17,
             'finished_at': SPLIT_TIMESTAMP4,
             'name': 'stage1',
             'started_at': SPLIT_TIMESTAMP1}]

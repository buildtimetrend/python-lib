#!/bin/bash
# Tests logging timestamps
#
# Usage : ./test/test_timestamp.sh
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

# get folder where script is located (bootstrap, init.sh will set BUILD_TREND_HOME)
BUILD_TREND_TEST=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

source $BUILD_TREND_TEST/../init.sh
echo "location of build-trend scripts : " $BUILD_TREND_HOME
echo

timestamp.sh stage1
echo "sleep 2 seconds"
sleep 2
timestamp.sh stage2
echo "sleep 5 seconds"
sleep 5
timestamp.sh stage3
echo "sleep 10 seconds"
sleep 10

echo
echo "timestamps"
cat $BUILD_TREND_LOGFILE
echo "analyse timestamps"
analyse.sh -l INFO -m native
cat $BUILD_TREND_OUTPUTFILE
echo "generate trend"
generate_trend.py --log=INFO --mode=native


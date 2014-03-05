#!/bin/bash
# Initialises variables and file needed for logging timestamps
#
# usage : source ./init.sh
#
# Copyright (C) 2014 Dieter Adriaenssens
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

BUILD_TREND_INIT=1
BUILD_TREND_HOME=`pwd`
BUILD_TREND_LOGFILE=$BUILD_TREND_HOME/timestamps.csv

export BUILD_TREND_INIT BUILD_TREND_HOME BUILD_TREND_LOGFILE

#cleanup previous logfile
if [ -f $BUILD_TREND_LOGFILE ]; then
    rm $BUILD_TREND_LOGFILE
fi


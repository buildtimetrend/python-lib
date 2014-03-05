#!/bin/bash
# Analyses the timestamps in the logfile
#
# usage : ./analyse.sh
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

if [ "$BUILD_TREND_INIT" == "1" ]; then
    cat $BUILD_TREND_LOGFILE
else
    echo "Build-trend not initialised, run 'source init.sh'"
fi

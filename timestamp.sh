#!/bin/bash
# Logs a timestamp to standard output and a logfile
#
# usage : ./timestamp.sh timestamp_name
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

# check if init.sh was run
if [ ! "$BUILD_TREND_INIT" == "1" ]; then
     echo "Buildtime-trend is not initialised, first run 'source init.sh'."
     exit 1
fi

VERBOSE=1

# parse command line options
while getopts ":qh" option; do
  case $option in
    q) VERBOSE=0 ;;
    h) echo "usage: $0 [-h] [-q] name"; exit ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# remove the options from the positional parameters
shift $(( OPTIND - 1 ))

# generate timestamp and log it
TIMESTAMP=$(date +%s)
if [ $VERBOSE -gt 0 ]; then
  echo "Timestamp $1 : $TIMESTAMP"
fi
echo "\"$1\",\"$TIMESTAMP\"" >> "$BUILD_TREND_LOGFILE"

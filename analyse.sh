#!/bin/bash
# Analyses the timestamps in the logfile
#
# usage : ./analyse.sh -m native,keen
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

# set default mode
mode=keen
logLevel=WARNING

# parse command line options
while getopts ":m:l:h" option; do
  case $option in
    m) mode=$OPTARG ;;
    l) logLevel=$OPTARG ;;
    h) echo "usage: $0 [-h] [-m native,keen] [-l DEBUG,INFO, WARNING, ERROR, CRITICAL]"; exit ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ "$BUILD_TREND_INIT" == "1" ]; then
    timestamp.sh -q end

    analyse.py --mode="$mode" --log="$logLevel"
else
    echo "Buildtime-trend is not initialised, first run 'source init.sh'."
fi

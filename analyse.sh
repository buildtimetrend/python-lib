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

# parse command line options
while getopts ":m:h" option; do
  case $option in
    m) mode=$OPTARG ;;
    h) echo "usage: $0 [-h] [-m native,keen]"; exit ;;
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
    if [[ "$TRAVIS" == "true" ]]; then
        # map $TRAVIS_TEST_RESULT to a more readable value
        case "$TRAVIS_TEST_RESULT" in
        0)
            test_result="passed"
            ;;
        1)
            test_result="failed"
            ;;
        *)
            test_result="errored"
            ;;
        esac
        analyse.py --mode="$mode" --ci="travis" --branch="$TRAVIS_BRANCH" --build="$TRAVIS_BUILD_NUMBER" --job="$TRAVIS_JOB_NUMBER" --repo="$TRAVIS_REPO_SLUG" --result="$test_result"
    else
	analyse.py --mode="$mode"
    fi
else
    echo "Buildtime-trend is not initialised, first run 'source init.sh'."
fi

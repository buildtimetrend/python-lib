#!/bin/bash
#
# Script to sync result of buildtimes analysis to a folder on Github pages (gh-pages).
# It is called by Travis CI, after each build.
#
# Usage ./sync-buildtime-trend-with-gh-pages.sh [-h] [-m native,keen]
#
# Based on a script originally written by maxiaohao in the aws-mock GitHub project,
# to update generated javadoc on the Github pages (gh-pages) of a project :
# https://github.com/treelogic-swe/aws-mock/blob/04746419b409e1689632da53a7ea6063dbe33ef8/.utility/push-javadoc-to-gh-pages.sh
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

# remove the options from the positional parameters
shift $(( OPTIND - 1 ))


# only run this script on Travis CI
# and if the initialise script (`source init.sh`) was run first
if [ "$TRAVIS" == "true" ] && [ "$BUILD_TREND_INIT" == "1" ]; then

  echo -e "Start synchronising buildtime-trend results on gh-pages..."
  
  GH_PAGES=$HOME/gh-pages

  # clone or update gh-pages dir
  if [ -d "$GH_PAGES" ]; then
    cd "$GH_PAGES"
    git pull --rebase
  else
    git clone --quiet --branch=gh-pages https://"$GH_TOKEN"@github.com/"$TRAVIS_REPO_SLUG" "$GH_PAGES" > /dev/null
    cd "$GH_PAGES"
  fi

  # set git user in gh-pages repo
  git config user.email "travis@travis-ci.org"
  git config user.name "travis-ci"

  GH_PAGES_BUILD_TREND_DIR=$GH_PAGES/buildtime-trend

  # create data dir if it doesn't exist
  if [ ! -d "$GH_PAGES_BUILD_TREND_DIR" ]; then
    mkdir -p "$GH_PAGES_BUILD_TREND_DIR"
  fi

  # set enviroment variable for the analysis result file
  # BUILD_TREND_OUTPUTFILE is used by the analysis script
  export BUILD_TREND_OUTPUTFILE=$GH_PAGES_BUILD_TREND_DIR/buildtimes.xml
  export BUILD_TREND_TRENDFILE=$GH_PAGES_BUILD_TREND_DIR/trend.png
  BUILD_TREND_OVERVIEWFILE=$GH_PAGES_BUILD_TREND_DIR/index.html
  BUILD_TREND_ORIGIN_OVERVIEWFILE=$BUILD_TREND_TRENDS_DIR/index.html
  BUILD_TREND_ASSETS=$GH_PAGES_BUILD_TREND_DIR/.
  BUILD_TREND_ORIGIN_ASSETS=$BUILD_TREND_TRENDS_DIR/assets
  export BUILD_TREND_CONFIGFILE=$GH_PAGES_BUILD_TREND_DIR/config.js
  export BUILD_TREND_SAMPLE_CONFIGFILE=$BUILD_TREND_TRENDS_DIR/config_sample.js

  # perform analysis
  analyse.sh -m "$mode" -l "$logLevel"
  # generate trend
  generate_trend.py --mode="$mode" --log="$logLevel"
  # update trends overview HTML and JavaScript file
  cp "$BUILD_TREND_ORIGIN_OVERVIEWFILE" "$BUILD_TREND_OVERVIEWFILE"
  cp -rf "$BUILD_TREND_ORIGIN_ASSETS" "$BUILD_TREND_ASSETS"

  # print trend location
  REPO_OWNER=${TRAVIS_REPO_SLUG%/*}
  REPO_NAME=${TRAVIS_REPO_SLUG#*/}
  echo "Trend located at : https://${REPO_OWNER}.github.io/${REPO_NAME}/buildtime-trend/index.html"

  # update buildtime trend data on gh-pages
  cd "$GH_PAGES"
  git add -f .
  git commit -m "buildtime-trend of build $TRAVIS_JOB_NUMBER synchronised with gh-pages"
  git push -fq origin gh-pages > /dev/null

  echo -e "Done synchronising buildtime-trend results on gh-pages."
fi

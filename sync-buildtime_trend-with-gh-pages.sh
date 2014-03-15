#!/bin/bash
#
# Script to sync result of buildtimes analysis to a folder on Github pages (gh-pages).
# It is called by Travis CI, after each build.
#
# Based on a script originally written by maxiaohao in the aws-mock GitHub project,
# to update generated javadoc on the Github pages (gh-pages) of a project :
# https://github.com/treelogic-swe/aws-mock/blob/04746419b409e1689632da53a7ea6063dbe33ef8/.utility/push-javadoc-to-gh-pages.sh
#
# Copyright 2014 Dieter Adriaenssens
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

if [ "$TRAVIS" == "true" ] && [ "$BUILD_TREND_INIT" == "1" ]; then

  echo -e "Start synchronising buildtime-trend results on gh-pages..."

  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "travis-ci"
  
  # clone or update gh-pages dir
  if [ -d $BUILD_TREND_HOME/gh-pages ]; then
    cd $BUILD_TREND_HOME/gh-pages
    git pull --rebase
  else
    cd $BUILD_TREND_HOME
    git clone --quiet --branch=gh-pages https://${GH_TOKEN}@github.com/${TRAVIS_REPO_SLUG} gh-pages > /dev/null
  fi

  GH_PAGES_BUILD_TREND_DIR=$BUILD_TREND_HOME/gh-pages/buildtime-trend

  # create data dir if it doesn't exist
  if [ ! -d $GH_PAGES_BUILD_TREND_DIR ]; then
    mkdir -p $GH_PAGES_BUILD_TREND_DIR
  fi

  BUILD_TREND_OUTPUTFILE=$GH_PAGES_BUILD_TREND_DIR/buildtimes.xml

  # perfom analysis
  analyse.sh

  # update buildtime trend data on gh-pages
  cd $BUILD_TREND_HOME/gh-pages
  git add -f .
  git commit -m "buildtime-trend of build $TRAVIS_JOB_NUMBER synchronised with gh-pages"
  git push -fq origin gh-pages > /dev/null

  echo -e "Done synchronising buildtime-trend results on gh-pages."
fi

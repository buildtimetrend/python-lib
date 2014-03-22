Build trend
===========

[![Build Status](https://travis-ci.org/ruleant/buildtime-trend.svg)](https://travis-ci.org/ruleant/buildtime-trend)
[![Coverage Status](https://coveralls.io/repos/ruleant/buildtime-trend/badge.png?branch=master)](https://coveralls.io/r/ruleant/buildtime-trend?branch=master)
[![Code Health](https://landscape.io/github/ruleant/buildtime-trend/master/landscape.png)](https://landscape.io/github/ruleant/buildtime-trend/master)
[![status](https://sourcegraph.com/api/repos/github.com/ruleant/buildtime-trend/badges/status.png)](https://sourcegraph.com/github.com/ruleant/buildtime-trend)

Create a trendline of the different stages of a build process

Dependencies
------------

- lxml (python wrapper for libxml2 and libxslt)

Install using pip :

`pip install lxml`

or as a Debian package :

`apt-get install python-lxml`

Usage
-----

First the timestamp recording needs to be initialised :

`source /path/to/init.sh`

This script will detect the location of the build-trend script folder,
adds it to the PATH and cleans logfiles of previous runs.
Executing the init script with `source` is required to be able to export environment variables to the current shell session.

Because the script dir is added to PATH, no path needs to be added
when logging a timestamp :

`timestamp.sh eventname`

This will log the current timestamp to a file and display it on STDOUT.
Repeat this step as much as needed.

When finished, run 

`analyse.sh`

to analyse the logfile with timestamps and print out the results.
It will calculate the duration between the timestamps and add them to
a file with the analysed data of previous builds.
When run on Travis CI, it will automatically add build/job related info.

License
-------

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

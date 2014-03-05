Build trend
===========

[![Build Status](https://travis-ci.org/ruleant/build-trend.png?branch=master)](https://travis-ci.org/ruleant/build-trend)

Create trends of a build process

Usage
-----

First the timestamp recording needs to be initialised :

`touch /path/to/init.sh`

This script will detect the location of the build-trend script folder,
adds it to the PATH and cleans logfiles of previous runs.

Because the script dir is added to PATH, no path needs to be added
when logging a timestamp :

`timestamp.sh eventname`

This will log the current timestamp to a file and display it on STDOUT.
Repeat this step as much as needed.

When finished, run 

`analyse.sh`

to analyse the logfile and print out the results.

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

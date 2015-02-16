Buildtime Trend Python library
==============================

Visualise what's trending in your build process

[![Buildtime trend](http://img.shields.io/badge/release-v0.2-blue.svg)](https://github.com/ruleant/buildtime-trend/releases/latest)
[![Buildtime trend](http://img.shields.io/badge/dev-v0.2--dev-blue.svg)](https://github.com/ruleant/buildtime-trend/zipball/master)
[![Build Status](https://travis-ci.org/buildtimetrend/python-lib.svg?branch=master)](https://travis-ci.org/buildtimetrend/python-lib)
[![Coverage Status](https://coveralls.io/repos/buildtimetrend/python-lib/badge.png?branch=master)](https://coveralls.io/r/buildtimetrend/python-lib?branch=master)
[![Code Health](https://landscape.io/github/buildtimetrend/python-lib/master/landscape.png)](https://landscape.io/github/buildtimetrend/python-lib/master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/buildtimetrend/python-lib/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/buildtimetrend/python-lib/?branch=master)
[![Codacy Badge](https://www.codacy.com/project/badge/38e1a8fcf164434f87389a693368d0f2)](https://www.codacy.com/public/ruleant/python-lib)

[![Buildtime trend](https://buildtimetrend-dev.herokuapp.com/badge/buildtimetrend/python-lib/latest)](http://ruleant.github.io/buildtime-trend/buildtime-trend/)
[![Total builds](https://buildtimetrend-dev.herokuapp.com/badge/buildtimetrend/python-lib/builds/month)](http://ruleant.github.io/buildtime-trend/buildtime-trend/)
[![Percentage passed build jobs](https://buildtimetrend-dev.herokuapp.com/badge/buildtimetrend/python-lib/passed/month)](http://ruleant.github.io/buildtime-trend/buildtime-trend/)

[![Stack Share](http://img.shields.io/badge/tech-stack-0690fa.svg)](http://stackshare.io/ruleant/buildtime-trend)
[![status](https://sourcegraph.com/api/repos/github.com/buildtimetrend/python-lib/.badges/status.svg)](https://sourcegraph.com/github.com/buildtimetrend/python-lib)


Features
--------

Visualise trends of build processes on Continuous Integration platforms by gathering and analysing build and timing data: 

- Capture timing data from each stage in a build process
- Store, analyse and create trends of the build process data
  - keen mode : send timing data to Keen.io and use the Keen.io API for analysis and visualisation
  - native mode : store data in xml format and use matplotlib to generate a chart (limited)
- Available charts and metrics :
  - number of builds, successful and failed
  - average build duration
  - duration of individual build stages
  - builds per branch
  - build duration per time of day/day of week

Usage
-----

The [Buildtime Trend Python client](https://github.com/buildtimetrend/python-client) and [Buildtime Trend as a Service](https://github.com/buildtimetrend/service) depend on this library.
It is recommended to use this library with either of them, have a look at their documentation on how to use them.

How to get it?
--------------

If you want to use this library directly, there are several ways of getting it.

Buildtimetrend library is registered in PyPI, to install, use :

```bash
pip install buildtimetrend
```

The [latest version](https://github.com/buildtimetrend/python-lib/releases/latest) is available for download as zip and tarball on GitHub. Unzip and copy to the desired directory.

If you prefer to use git, several options are available :

- development version : `git clone https://github.com/buildtimetrend/python-lib.git`
- latest release : `git clone https://github.com/buildtimetrend/python-lib.git --branch release`
- a specific release : `git clone https://github.com/buildtimetrend/python-lib.git --branch v0.1.2`

Dependencies
------------

- `python` : Python 2.7
- `keen` : client for storing build time data as events in Keen.io
- `python-dateutil` : for formatting datetime objects
- `lxml` : python wrapper for libxml2 and libxslt
- `pyyaml` : for parsing the config file in yaml format
- native mode :
  - `matplotlib` (v1.2.0 or higher) : for drawing the `native` trend graph, can be omitted when only using Keen.io to generate charts. Stackplot requires version v1.2.0

### Dependency installation

- using the setup script

`python setup.py install`

- if you want to use `native` mode to store data or generate charts  :

`python setup.py install -e .[native]`

- install each dependency individually :

```
pip install keen
pip install python-dateutil
pip install pyyaml
pip install lxml
pip install 'matplotlib>=1.2.0'
```


Store build time data in xml (native mode)
------------------------------------------

See wiki for [data schema of the xml file](https://github.com/buildtimetrend/python-lib/wiki/Structure#data-file-in-native-mode).


Store build time data in Keen.io
--------------------------------

See wiki for [data schema of data sent to Keen.io](https://github.com/buildtimetrend/python-lib/wiki/Structure#data-structures-in-keen-mode).


Bugs and feature requests
-------------------------

Please report bugs and add feature requests in the Github [issue tracker](https://github.com/buildtimetrend/python-lib/issues).


Credits
-------

For an overview of who contributed to create Buildtime trend, see [Credits](https://github.com/buildtimetrend/python-lib/wiki/Credits).

Contact
-------

Website : https://buildtimetrend.github.io/

Mailinglist : [Buildtime Trend Community](https://groups.google.com/d/forum/buildtimetrend-dev)

Follow us on [Twitter](https://twitter.com/buildtime_trend), [Github](https://github.com/buildtimetrend/python-lib) and [OpenHub](https://www.openhub.net/p/buildtime-trend).


License
-------

Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This software was originally released under GNU General Public License version 3 or any later version, all commits contributed from 27th of November 2014 on, are contributed as GNU Affero General Public License. Hence the project is considered to be GNU Affero General Public License from 27th of November 2014 on.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

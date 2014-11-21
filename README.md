Buildtime trend
===============

Visualise what's trending in your build process

[![Buildtime trend](http://img.shields.io/badge/release-v0.1.2-blue.svg)](https://github.com/ruleant/buildtime-trend/releases/latest)
[![Buildtime trend](http://img.shields.io/badge/dev-v0.2--dev-blue.svg)](https://github.com/ruleant/buildtime-trend/zipball/master)
[![Build Status](https://travis-ci.org/ruleant/buildtime-trend.svg)](https://travis-ci.org/ruleant/buildtime-trend)
[![Coverage Status](https://coveralls.io/repos/ruleant/buildtime-trend/badge.png?branch=master)](https://coveralls.io/r/ruleant/buildtime-trend?branch=master)
[![Code Health](https://landscape.io/github/ruleant/buildtime-trend/master/landscape.png)](https://landscape.io/github/ruleant/buildtime-trend/master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ruleant/buildtime-trend/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ruleant/buildtime-trend/?branch=master)
[![Buildtime trend](http://img.shields.io/badge/buildtime-trend-blue.svg)](http://ruleant.github.io/buildtime-trend/buildtime-trend/)
[![Stack Share](http://img.shields.io/badge/tech-stack-0690fa.svg?style=flat)](http://stackshare.io/ruleant/buildtime-trend)
[![status](https://sourcegraph.com/api/repos/github.com/ruleant/buildtime-trend/badges/status.png)](https://sourcegraph.com/github.com/ruleant/buildtime-trend)


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

How to get it?
--------------

The [latest version](https://github.com/ruleant/buildtime-trend/releases/latest) is available for download as zip and tarball on GitHub. Unzip and copy to the desired directory.

If you prefer to use git, several options are available :

- development version : `git clone https://github.com/ruleant/buildtime-trend.git`
- latest release : `git clone https://github.com/ruleant/buildtime-trend.git --branch release`
- a specific release : `git clone https://github.com/ruleant/buildtime-trend.git --branch v0.1.2`

Dependencies
------------

- `keen` : client for storing build time data as events in Keen.io
- `python-dateutil` : for formatting datetime objects
- `lxml` : python wrapper for libxml2 and libxslt
- `pyyaml` : for parsing the config file in yaml format
- `matplotlib` (v1.2.0 or higher) : for drawing the `native` trend graph, can be omitted when only using Keen.io to generate charts. Stackplot requires version v1.2.0

### Dependency installation

- using pip :

`pip install -r requirements.txt`

- if you want to store data or generate charts in `native` mode :

`pip install -r requirements-native.txt`

- install each dependency individually :

```
pip install keen
pip install python-dateutil
pip install pyyaml
pip install lxml
pip install 'matplotlib>=1.2.0'
```

- install as a Debian package :

`apt-get install python-lxml python-dateutil python-yaml`

Keen.io client and the required matplotlib version are not available as Debian packages, so look at the `pip` instructions above

Usage
-----

First the timestamp recording needs to be initialised :

`source /path/to/init.sh`

This script will detect the location of the build-trend script folder,
adds it to the PATH and cleans logfiles of previous runs.
Executing the init script with `source` is required to export environment variables to the current shell session.

Because the script dir is added to PATH, no path needs to be added
when logging a timestamp :

`timestamp.sh event_name`

This will log the current timestamp to a file and display it on STDOUT.
Repeat this step as much as needed.

When all build stages are finished, run

`timestamp.sh end` (optional, `analyse.sh` adds it automatically)

followed by

`analyse.sh`

which will analyse the logfile with timestamps and print out the results.
The `analyse.sh` script will calculate the duration between the timestamps and add those to a file with the analysed data of previous builds.
When the analysis script encounters the `end` timestamp, it will stop analysing the timestamp file and return the duration of the build stages. Possible event names ending the analysis are : `end`, `done`, `finished` or `completed`.

When Keen.io is enabled, the data will be sent to your Keen.io project for analysis.

When run on Travis CI, it will automatically add build/job related info.
Parameter `-m native` will store data in xml format. It is recommended to use Keen.io to store data, see below for details.

To generate a graph from previous builds, run

`generate_trend.py`

It will take the file with analysed data generated by the analyse script and turn it into a trend graph and saves this graph.
Parameter `--mode=native` will create a trend using Python `matplotlib`. It is recommended to use Keen.io to generate graphs, see below for details.
If Keen.io is enabled, `generate_trend.py` can be run without parameters.

Use the `sync-buildtime-trend-with-gh-pages.sh` script when you run it as part of a Travis CI build. See below for details.

Store build time data in xml (native mode)
------------------------------------------

(It is recommended to use Keen.io to store data and generate trends, see below)

To store data in xml, native mode needs to be enabled. The xml file is stored in `trends/buildtimes.xml` by default.

To analyse timestamps and store the analysed data :

`analyse.sh -m native`

See wiki for [data schema of the xml file](https://github.com/ruleant/buildtime-trend/wiki/Structure#data-file-in-native-mode).

To generate a chart from the data stored in the xml file :

`generate_trend.py --mode=native`

This will save a trend image in `trends/trend.png`

Store build time data in Keen.io
--------------------------------

Next to storing your build time data in xml, it can be sent to Keen.io for storage, analysis and generating graphs.

Follow these steps to enable using Keen.io :

1. [Create a Keen.io account](https://keen.io/signup), if you haven't already done so.
2. [Create a project](https://keen.io/add-project) in your Keen.io account.
3. Look up the `project ID`, `Write Key` and `Master key` and assign them to environment variables :
- `export KEEN_PROJECT_ID=<Project ID>`
- `export KEEN_WRITE_KEY=<Write Key>` (when running on Travis CI, use `Master Key`, see below)
- `export KEEN_MASTER_KEY=<Master Key>`

If these environment variables are set, the scripts will detect this and use Keen.io to store data, do analysis and generate graphs.

See wiki for [data schema of data sent to Keen.io](https://github.com/ruleant/buildtime-trend/wiki/Structure#data-structures-in-keen-mode).

Visualise the trends (powered by Keen.io)
-----------------------------------------

Multiple trends are available when data was stored in `keen` mode :

Folder `trends` contains all files necessary to display the generated trends.
- Copy folder `trends` to the desired location
- Rename (or copy) `config_sample.js` to `config.js`
- Edit `config.js` :
  - add `keen_project_id` (see Keen.io section above)
  - add `keen_read_key` (see Keen.io section above, or generate a scoped read key with `get_read_key.py project_name` (`project_name` should be the same as the project_name used to store the data, this is usually the git-repo name, fe. `ruleant/buildtime-trend`)
  - add `project_name` : repo name is a good default, but it can be custom project name as well, this is only used as title on the webpage. It is not used to collect data.
- Browse to `trends/index.html`, this should display the trends

If you are building a Github repo on Travis CI, and you have `gh-pages` branch, you can use the script mentioned below to automatically add the right files and create the config file.


Integrate with Travis CI
------------------------

You can integrate Buildtime Trend with your build process on Travis CI :
install and initialise the buildtime trend scripts, add timestamp labels, generate the trend
and synchronise it with your gh-pages branch.

All you need is a github repo, a Travis CI account for your repo and a gh-pages branch to publish the results.

You also need to create an encrypted GH_TOKEN to get write access to your repo (publish results on gh-pages branch) :
- [create](https://github.com/settings/applications) the access token for your github repo, `repo` scope is sufficient
- encrypt the environment variable using the [Travis CI command line tool](http://docs.travis-ci.com/user/encryption-keys/) :
`travis encrypt GH_TOKEN=github_access_token`
- add the encrypted token to your `.travis.yml` file (see below)

To enable integration with Keen.io, `KEEN_PROJECT_ID` and `KEEN_WRITE_KEY` should be set (see above):

1. Follow the steps above to create a Keen.io account and project and look up the `Project ID` and `Master Key`
2. Assign the `Project ID` and `Master Key` to the corresponding environment variables and encrypt them using the [Travis CI command line tool](http://docs.travis-ci.com/user/encryption-keys/) and add it them to `.travis.yml` (see below) :
- `travis encrypt KEEN_PROJECT_ID=<Project ID>`
- `travis encrypt KEEN_WRITE_KEY=<Master Key>`
**Remark :** Use the `Master Key` instead of the `Write Key` of your Keen.io project, because the `Write Key` is too long to encrypt using the Travis CI encryption tool
- `travis encrypt KEEN_MASTER_KEY=<Master Key>`
The `Master Key` of your Keen.io project is used to generate a scoped read key

The generated trend graph and build-data will be put in folder `buildtime-trend` on your `gh-pages` branch.
The trend is available on http://{username}.github.io/{repo_name}/buildtime-trend/index.html

Example `.travis.yml` file :

    language: python
    env:
      global:
        - secure: # your secure GH_TOKEN goes here (required to share trend on gh-pages)
        - secure: # your secure KEEN_PROJECT_ID goes here (required to store data on Keen.io)
        - secure: # your secure KEEN_WRITE_KEY goes here (required to store data on Keen.io)
        - secure: # your secure KEEN_MASTER_KEY goes here (required to generate a scoped read key to generate graphs using the Keen.io API)
    before_install:
      # install and initialise build-trend scripts
      # uncomment one of two options below (stable or development)
      # download latest stable release
      - git clone --depth 1 --branch v0.1.2 https://github.com/ruleant/buildtime-trend.git $HOME/buildtime-trend
      # use latest development version (clone git repo)
      # - if [[ -d $HOME/buildtime-trend/.git ]]; then cd $HOME/buildtime-trend; git pull; cd ..; else git clone https://github.com/ruleant/buildtime-trend.git $HOME/buildtime-trend; fi
      # initialise buildtime-trend scripts
      - source $HOME/buildtime-trend/init.sh
    install:
      # generate timestamp with label 'install'
      - timestamp.sh install
      # install buildtime-trend dependencies
      - CFLAGS="-O0" pip install -r ${BUILD_TREND_HOME}/requirements.txt
      # install dependencies
    script:
      # generate timestamp with label 'tests'
      - timestamp.sh tests
      # run your tests
    after_script:
      # synchronise buildtime-trend result with gh-pages
      - sync-buildtime-trend-with-gh-pages.sh

Run `sync-buildtime-trend-with-gh-pages.sh` in `after_script` to report the gathered timestamps with the result of the build in `$TRAVIS_TEST_RESULT`, which comes available in `after_{success|failure}`. `after_script` is executed regardless of the build result, so after both `after_success` and `after_failure`.

To enable `native` mode, add `-m native` when calling `sync-buildtime-trend-with-gh-pages.sh`

Bugs and feature requests
-------------------------

Please report bugs and add feature requests in the Github [issue tracker](https://github.com/ruleant/buildtime-trend/issues).


Credits
-------

For an overview of who contributed to create Buildtime trend, see [Credits](https://github.com/ruleant/buildtime-trend/wiki/Credits).

Contact
-------

Website : http://ruleant.github.io/buildtime-trend

Follow us on [Twitter](https://twitter.com/buildtime_trend), [Github](https://github.com/ruleant/buildtime-trend) and [OpenHub](https://www.openhub.net/p/buildtime-trend).


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

'''
vim: set expandtab sw=4 ts=4:

Interface to Keen IO.

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtime-trend
<https://github.com/ruleant/buildtime-trend/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import os


def keen_io_writable():
    '''
    Check if login keys for Keen IO API are set, to allow writing.
    '''
    if "KEEN_PROJECT_ID" in os.environ and "KEEN_WRITE_KEY" in os.environ:
        return True
    return False


def keen_io_readable():
    '''
    Check if login keys for Keen IO API are set, to allow reading.
    '''
    if "KEEN_PROJECT_ID" in os.environ and "KEEN_READ_KEY" in os.environ:
        return True
    return False

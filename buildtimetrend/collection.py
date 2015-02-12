# vim: set expandtab sw=4 ts=4:
"""
Dictionary based collection class.

Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/python-lib
<https://github.com/buildtimetrend/python-lib/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import copy
from buildtimetrend.tools import check_dict


class Collection(object):

    """ Dictionary based collection object. """

    def __init__(self):
        """ Initialize instance. """
        self.items = {}

    def add_item(self, name, value):
        """
        Add an item to the collection.

        Parameters :
        - name : Item name
        - value : Item value
        """
        self.items[name] = value

    def get_item(self, name):
        """
        Get an item from a collection.

        Parameters :
        - name : Item name
        """
        if name in self.items:
            return self.items[name]
        else:
            return None

    def get_size(self):
        """ Get collection size. """
        return len(self.items)

    def add_items(self, items_dict):
        """
        Add items as a dictionary to the collection.

        Parameters:
        - items_dict : dictionary with items
        """
        if check_dict(items_dict, "items_dict"):
            # append dictionary with items to the existing collection
            self.items.update(items_dict)

    def get_items(self):
        """ Return items collection as dictionary. """
        # copy values of items collection
        return copy.deepcopy(self.items)

# vim: set expandtab sw=4 ts=4:
"""
Travis Substage class.

Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>

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
from buildtimetrend import logger
from buildtimetrend.stages import Stage
from buildtimetrend.tools import check_dict


class TravisSubstage(object):

    """
    Travis CI substage object.

    It is constructed by feeding parsed tags from Travis CI logfile.
    """

    def __init__(self):
        """Initialise Travis CI Substage object."""
        self.stage = Stage()
        self.timing_hash = ""
        self.finished_incomplete = False
        self.finished = False

    def process_parsed_tags(self, tags_dict):
        """
        Process parsed tags and calls the corresponding handler method.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        result = False

        # check if parameter tags_dict is a dictionary
        if check_dict(tags_dict, "tags_dict"):
            if 'start_stage' in tags_dict:
                result = self.process_start_stage(tags_dict)
            elif 'start_hash' in tags_dict:
                result = self.process_start_time(tags_dict)
            elif 'command' in tags_dict:
                result = self.process_command(tags_dict)
            elif 'end_hash' in tags_dict:
                result = self.process_end_time(tags_dict)
            elif 'end_stage' in tags_dict:
                result = self.process_end_stage(tags_dict)

        return result

    def process_start_stage(self, tags_dict):
        """
        Process parsed start_stage tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'start_stage', 'start_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger.debug("Start stage : %s", tags_dict)

        result = False

        if self.has_started():
            logger.info("Substage already started")
        else:
            name = "{stage:s}.{substage:s}".format(
                stage=tags_dict['start_stage'],
                substage=tags_dict['start_substage']
            )
            result = self.set_name(name)

        return result

    def process_start_time(self, tags_dict):
        """
        Process parsed start_time tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'start_hash'):
            return False

        logger.debug("Start time : %s", tags_dict)

        if self.has_timing_hash():
            logger.info("Substage timing already set")
            return False

        self.timing_hash = tags_dict['start_hash']
        logger.info("Set timing hash : %s", self.timing_hash)

        return True

    def process_command(self, tags_dict):
        """
        Process parsed command tag.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'command'):
            return False

        logger.debug("Command : %s", tags_dict)

        result = False

        if self.has_command():
            logger.info("Command is already set")
        elif self.stage.set_command(tags_dict['command']):
            logger.info("Set command : %s", tags_dict['command'])
            result = True

        return result

    def process_end_time(self, tags_dict):
        """
        Process parsed end_time tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({
            'end_hash',
            'start_timestamp',
            'finish_timestamp',
            'duration'
        })
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger.debug("End time : %s", tags_dict)

        result = False

        # check if timing was started
        # and if hash matches
        if (not self.has_timing_hash() or
                self.timing_hash != tags_dict['end_hash']):
            logger.info("Substage timing was not started or"
                        " hash doesn't match")
            self.finished_incomplete = True
        else:
            set_started = set_finished = set_duration = False

            # Set started timestamp
            if self.stage.set_started_at_nano(tags_dict['start_timestamp']):
                logger.info("Stage started at %s",
                            self.stage.data["started_at"]["isotimestamp"])
                set_started = True

            # Set finished timestamp
            if self.stage.set_finished_at_nano(tags_dict['finish_timestamp']):
                logger.info("Stage finished at %s",
                            self.stage.data["finished_at"]["isotimestamp"])
                set_finished = True

            # Set duration
            if self.stage.set_duration_nano(tags_dict['duration']):
                logger.info("Stage duration : %ss",
                            self.stage.data['duration'])
                set_duration = True

            result = set_started and set_finished and set_duration

        return result

    def process_end_stage(self, tags_dict):
        """
        Process parsed end_stage tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'end_stage', 'end_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger.debug("End stage : %s", tags_dict)

        # construct substage name
        end_stagename = "{stage}.{substage}".format(
            stage=tags_dict['end_stage'],
            substage=tags_dict['end_substage']
        )

        # check if stage was started
        # and if substage name matches
        if not self.has_name() or self.stage.data["name"] != end_stagename:
            logger.info("Substage was not started or name doesn't match")
            self.finished_incomplete = True
            return False

        # stage finished successfully
        self.finished = True
        logger.info("Stage %s finished successfully", self.get_name())

        return True

    def get_name(self):
        """
        Return substage name.

        If name is not set, return the command.
        """
        if self.has_name():
            return self.stage.data["name"]
        elif self.has_command():
            return self.stage.data["command"]
        else:
            return ""

    def set_name(self, name):
        """
        Set substage name.

        Parameters:
        - name : substage name
        """
        return self.stage.set_name(name)

    def has_name(self):
        """
        Check if substage has a name.

        Returns true if substage has a name
        """
        return "name" in self.stage.data and \
            self.stage.data["name"] is not None and \
            len(self.stage.data["name"]) > 0

    def has_timing_hash(self):
        """
        Check if substage has a timing hash.

        Returns true if substage has a timing hash
        """
        return self.timing_hash is not None and len(self.timing_hash) > 0

    def has_command(self):
        """
        Check if a command is set for substage.

        Returns true if a command is set
        """
        return "command" in self.stage.data and \
            self.stage.data["command"] is not None and \
            len(self.stage.data["command"]) > 0

    def get_command(self):
        """Return substage command."""
        if self.has_command():
            return self.stage.data["command"]
        else:
            return ""

    def has_started(self):
        """
        Check if substage has started.

        Returns true if substage has started
        """
        return self.has_name() or self.has_timing_hash() or self.has_command()

    def has_finished(self):
        """
        Check if substage has finished.

        A substage is finished, if either the finished_timestamp is set,
        or if finished is (because of an error in parsing the tags).

        Returns true if substage has finished
        """
        return self.finished_incomplete or \
            self.has_name() and self.finished or \
            not self.has_name() and self.has_timing_hash() and \
            "finished_at" in self.stage.data or \
            not self.has_name() and not self.has_timing_hash() and \
            self.has_command()

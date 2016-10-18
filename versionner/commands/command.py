"""
Abstract class for commands
"""

from collections import namedtuple


# pylint: disable=too-few-public-methods,missing-docstring
from versionner import config


class Command:
    def __init__(self, cfg:config.Config):
        self.cfg = cfg

    def execute(self):
        return self.run()

    def run(self):
        """
        Abstract method for executing commands
        @return:
        """
        raise NotImplementedError("Not implemented yet...")


CommandOutput = namedtuple('CommandOutput', ('modified_files', 'current_version'))

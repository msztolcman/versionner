"""
Abstract class for commands
"""

from collections import namedtuple


# pylint: disable=too-few-public-methods,missing-docstring
from versionner import config


class CommandOutput(namedtuple('CommandOutput', ['current_version', 'modifications', 'modified_files'])):
    def __new__(cls, current_version, modifications=None, modified_files=None):
        return super(CommandOutput, cls).__new__(cls, current_version, modifications, modified_files)


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

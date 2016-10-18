"""
Abstract class for commands
"""


# pylint: disable=too-few-public-methods,missing-docstring
from versionner import config
from versionner import version


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

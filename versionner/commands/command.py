"""Abstract class for commands"""

from collections import namedtuple


class CommandOutput(namedtuple('CommandOutput', ['current_version', 'modifications', 'modified_files'])):
    """Output structure for Command.execute result"""
    def __new__(cls, current_version, modifications=None, modified_files=None):
        return super(CommandOutput, cls).__new__(cls, current_version, modifications, modified_files)


class Command:
    """Abstract class for commands"""
    def __init__(self, cfg):
        self.cfg = cfg

    def execute(self):
        """Main method for executing commands.

        :return:
        """
        return self.run()

    def run(self):
        """Abstract method for executing commands.
        Shouldn't be executed directly, use Command.execute

        @return:
        """
        raise NotImplementedError("Not implemented yet...")

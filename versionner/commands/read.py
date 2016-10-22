"""Class for command: read"""

from versionner.commands import Command, CommandOutput
from versionner import version


class Read(Command):
    """Realize tasks for 'read' command"""
    def run(self):
        version_file = version.VersionFile(self.cfg.version_file)

        current = version_file.read()

        return CommandOutput(current)

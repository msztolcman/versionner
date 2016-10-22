"""Class for command: up"""

from versionner.commands import Command, CommandOutput
from versionner import version
from versionner.commands.files_management import save_version_and_update_files

class Up(Command):
    """Realize tasks for 'up' command"""
    def run(self):
        version_file = version.VersionFile(self.cfg.version_file)

        current = version_file.read()

        new = current.up(self.cfg.up_part, self.cfg.value)

        modified_files = save_version_and_update_files(self.cfg, version_file, new)

        return CommandOutput(new, modified_files['changes'], modified_files['files'])

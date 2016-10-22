"""Class for command: init"""

from versionner.commands import Command, CommandOutput
from versionner import version
from versionner.commands.files_management import save_version_and_update_files

class Init(Command):
    """Realize tasks for 'init' command"""
    def run(self):
        version_file = version.VersionFile(self.cfg.version_file)

        try:
            current = version.Version(self.cfg.value)
        except ValueError as exc:
            raise version.InvalidVersionError("Cannot parse version string: %s" % self.cfg.value) from exc

        modified_files = save_version_and_update_files(self.cfg, version_file, current)

        return CommandOutput(current, modified_files['changes'], modified_files['files'])

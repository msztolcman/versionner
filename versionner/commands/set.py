"""Class for command: set"""

from versionner.commands import Command, CommandOutput
from versionner import version
from versionner.commands.files_management import save_version_and_update_files


class Set(Command):
    """Realize tasks for 'set' command"""
    def run(self):
        version_file = version.VersionFile(self.cfg.version_file)
        current = version_file.read()

        if isinstance(self.cfg.value, tuple):
            new = version.Version(current)

            try:
                for field, value in zip(version.Version.VALID_FIELDS, self.cfg.value):
                    if value is not None:
                        new = new.set(field, value)
            except ValueError as exc:
                raise version.InvalidVersionError("Cannot use \"%s\" as \"--%s\" field" % (value, field)) from exc
        else:
            try:
                new = version.Version(self.cfg.value)
            except ValueError as exc:
                raise version.InvalidVersionError("Cannot parse version string: %s" % self.cfg.value) from exc

        modified_files = save_version_and_update_files(self.cfg, version_file, new)

        return CommandOutput(new, modified_files['changes'], modified_files['files'])

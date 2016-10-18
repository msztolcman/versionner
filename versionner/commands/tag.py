import traceback

from versionner.commands import Command
from versionner import version
from versionner import vcs


class Tag(Command):
    """Realize tasks for 'tag' command"""
    def run(self):
        version_file = version.VersionFile(self.cfg.version_file)

        current = version_file.read()
        try:
            vcs_handler = vcs.VCS(self.cfg.vcs_engine)
            vcs_handler.create_tag(current, self.cfg.vcs_tag_params)
        # pylint: disable=bare-except
        except:
            print('Git tag failed, do it yourself')
            if self.cfg.verbose:
                traceback.print_exc()
        else:
            print('Git tag created')

        return {'current_version': current, 'quant': 0}

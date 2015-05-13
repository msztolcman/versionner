import subprocess

from versionner import defaults

class VCS(object):
    def __init__(self, engine):
        self._engine = engine

    def get_command(self, version, params):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'tag', '-a', '-m', 'v%s' % version, str(version)]
            if params:
                cmd.extend(params)

        if not cmd:
            raise RuntimeError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def create_tag(self, version, params):
        cmd = self.get_command(version, params)

        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if p.returncode:
            raise RuntimeError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (version, p.returncode, stderr))

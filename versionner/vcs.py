"""
    Version Control Systems abstractions
"""

import subprocess

from versionner import defaults


# pylint: disable=too-few-public-methods
class VCS(object):
    """
        Main class for working with VCS
    """

    def __init__(self, engine):
        """
        Initializer, just save 'engine' option

        :param engine:
        :return:
        """
        self._engine = engine

    def _get_command(self, version, params):
        """
        Build and return full command to use with subprocess.Popen

        :param version:
        :param params:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'tag', '-a', '-m', 'v%s' % version, str(version)]
            if params:
                cmd.extend(params)

        if not cmd:
            raise RuntimeError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def create_tag(self, version, params):
        """
        Run VCS command for tag using subprocess.Popen

        :param version:
        :param params:
        :return:
        """
        cmd = self._get_command(version, params)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # pylint: disable=unexpected-keyword-arg
        (_, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise RuntimeError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (
                version, process.returncode, stderr))

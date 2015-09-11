"""
    Version Control Systems abstractions
"""

import subprocess

from versionner import defaults


class VCSError(RuntimeError): pass


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

    def _get_tag_command(self, version, params):
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
        cmd = self._get_tag_command(version, params)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # pylint: disable=unexpected-keyword-arg
        (_, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise RuntimeError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (
                version, process.returncode, stderr))

    def _get_status_command(self):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'status', '--porcelain']

        if not cmd:
            raise RuntimeError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def raise_if_cant_commit(self):
        cmd = self._get_status_command()

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise RuntimeError('Can\'t verify VCS status. Process exited with code %d and message: %s' % (
                process.returncode, stderr))

        for line in stdout.splitlines():
            if line.decode('utf-8').startswith(('??', '!!')):
                continue
            raise VCSError("VCS status doesn't allow to commit. Please commit or stash your changes and try again")

    def _get_commit_command(self, message):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'commit', '-m', message]

        if not cmd:
            raise RuntimeError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def create_commit(self, message):
        cmd = self._get_commit_command(message)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise RuntimeError('Commit failed. Process exited with code %d and message: %s' % (
                process.returncode, stderr))

    def _get_add_command(self, paths):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'add'] + list(paths)

        if not cmd:
            raise RuntimeError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def add_to_stage(self, paths):
        cmd = self._get_add_command(paths)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise RuntimeError('Can\'t verify VCS status. Process exited with code %d and message: %s' % (
                process.returncode, stderr))

        for line in stdout.splitlines():
            if line.decode('utf-8').startswith(('??', '!!')):
                continue
            raise VCSError("VCS status doesn't allow to commit. Please commit or stash your changes and try again")

"""
    Version Control Systems abstractions
"""

import subprocess

from versionner import defaults


class VCSError(RuntimeError):
    pass


class UnknownVCSError(VCSError):
    pass


class VCSCommandsBuilder:
    def __init__(self, engine):
        self._engine = engine

    def tag(self, version, params):
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
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def status(self):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'status', '--porcelain']

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def commit(self, message):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'commit', '-m', message]

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def add(self, paths):
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'add'] + list(paths)

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd


# pylint: disable=too-few-public-methods
class VCS:
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
        self._command = VCSCommandsBuilder(engine)

    def create_tag(self, version, params):
        """
        Run VCS command for tag using subprocess.Popen

        :param version:
        :param params:
        :return:
        """
        cmd = self._command.tag(version, params)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # pylint: disable=unexpected-keyword-arg
        (_, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise VCSError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (
                version, process.returncode, stderr.decode('utf-8')))

    def raise_if_cant_commit(self):
        cmd = self._command.status()

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise VCSError('Can\'t verify VCS status. Process exited with code %d and message: %s' % (
                process.returncode, stderr))

        for line in stdout.splitlines():
            if line.decode('utf-8').startswith(('??', '!!')):
                continue
            raise VCSError("VCS status doesn't allow to commit. Please commit or stash your changes and try again")

    def create_commit(self, message):
        cmd = self._command.commit(message)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise VCSError('Commit failed. Process exited with code %d and message: %s' % (
                process.returncode, stderr.decode('utf-8')))

    def add_to_stage(self, paths):
        cmd = self._command.add(paths)

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_TAG_TIMEOUT)

        if process.returncode:
            raise VCSError('Can\'t add paths to VCS. Process exited with code %d and message: %s' % (
                process.returncode, stderr))

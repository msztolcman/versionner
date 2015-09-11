"""
    Version Control Systems abstractions
"""

import subprocess

from versionner import defaults


class VCSError(RuntimeError):
    """General VCS error"""


class UnknownVCSError(VCSError):
    """Unknwon VCS"""


class VCSStateError(VCSError):
    """VCS state doesn't allow for specified command"""


class VCSCommandsBuilder:
    """ Build shell VCS command
    """
    def __init__(self, engine):
        self._engine = engine

    def tag(self, version, params):
        """
        Build and return full command to use with subprocess.Popen for 'git tag' command

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
        """
        Build and return full command to use with subprocess.Popen for 'git status' command

        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'status', '--porcelain']

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def commit(self, message):
        """
        Build and return full command to use with subprocess.Popen for 'git commit' command

        :param message:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'commit', '-m', message]

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def add(self, paths):
        """
        Build and return full command to use with subprocess.Popen for 'git add' command

        :param paths:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'add'] + list(paths)

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd


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

    @staticmethod
    def _exec(cmd):
        """
        Execute command using subprocess.Popen
        :param cmd:
        :return: (code, stdout, stderr)
        """
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # pylint: disable=unexpected-keyword-arg
        (stdout, stderr) = process.communicate(timeout=defaults.DEFAULT_VCS_TIMEOUT)

        return process.returncode, stdout.decode(), stderr.decode()

    def create_tag(self, version, params):
        """
        Run VCS command for tag using subprocess.Popen

        :param version:
        :param params:
        :return:
        """
        cmd = self._command.tag(version, params)

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise VCSError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (
                version, code, stderr or stdout))

    def raise_if_cant_commit(self):
        """
        Verify VCS status and raise an error if commit is disallowed

        :return:
        """
        cmd = self._command.status()

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise VCSError('Can\'t verify VCS status. Process exited with code %d and message: %s' % (
                code, stderr or stdout))

        for line in stdout.splitlines():
            if line.startswith(('??', '!!')):
                continue
            raise VCSStateError("VCS status doesn't allow to commit. Please commit or stash your changes and try again")

    def create_commit(self, message):
        """
        Create commit

        :param message:
        :return:
        """
        cmd = self._command.commit(message)

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise VCSError('Commit failed. Process exited with code %d and message: %s' % (
                code, stderr or stdout))

    def add_to_stage(self, paths):
        """
        Stage given files

        :param paths:
        :return:
        """
        cmd = self._command.add(paths)

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise VCSError('Can\'t add paths to VCS. Process exited with code %d and message: %s' % (
                code, stderr + stdout))

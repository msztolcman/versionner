import importlib
import subprocess

from versionner import defaults
from versionner.vcs import errors


class VCS:
    """
        Main class for working with VCS
    """

    def __init__(self, engine):
        """
        Initializer

        :param engine:
        :return:
        """
        self._engine = engine

        try:
            builder = importlib.import_module(engine, 'vcs')
        except ImportError:
            raise errors.UnknownVCSError("Unknown VCS engine: %s" % engine)

        self._command = builder.VCSCommandsBuilder()

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
            raise errors.VCSError('Can\'t create VCS tag %s. Process exited with code %d and message: %s' % (
                version, code, stderr or stdout))

    def raise_if_cant_commit(self):
        """
        Verify VCS status and raise an error if commit is disallowed

        :return:
        """
        cmd = self._command.status()

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise errors.VCSError('Can\'t verify VCS status. Process exited with code %d and message: %s' % (
                code, stderr or stdout))

        for line in stdout.splitlines():
            if line.startswith(('??', '!!')):
                continue
            raise errors.VCSStateError("VCS status doesn't allow to commit. Please commit or stash your changes and try again")

    def create_commit(self, message):
        """
        Create commit

        :param message:
        :return:
        """
        cmd = self._command.commit(message)

        (code, stdout, stderr) = self._exec(cmd)

        if code:
            raise errors.VCSError('Commit failed. Process exited with code %d and message: %s' % (
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
            raise errors.VCSError('Can\'t add paths to VCS. Process exited with code %d and message: %s' % (
                code, stderr + stdout))

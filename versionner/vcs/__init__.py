"""Contains VCS class that is abstraction for VCS actions"""

import importlib
import re

from versionner.vcs import errors


class VCS:
    """VCS abstraction layer.
    Imports module engine, and proxy calls into it
    """
    def __init__(self, engine):
        """Import engine module."""
        self._engine = engine

        if engine.startswith('_') or engine.endswith('_') or not re.match(r'^\w+$', engine, re.UNICODE):
            raise errors.UnknownVCSError("Incorrect engine name: %s" % engine)

        try:
            builder = importlib.import_module('versionner.vcs.%s' % engine)
        except ImportError:
            raise errors.UnknownVCSError("Unknown VCS engine: %s" % engine)

        self._command = builder.VCSEngine()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def create_tag(self, version, params):
        """Create VCS tag

        :param version:
        :param params:
        :return:
        """
        return self._command.create_tag(version, params)

    def raise_if_cant_commit(self):
        """Verify VCS status and raise an error if commit is disallowed

        :return:
        """
        return self._command.raise_if_cant_commit()

    def create_commit(self, message):
        """Create commit

        :param message:
        :return:
        """
        return self._command.create_commit(message)

    def add_to_stage(self, paths):
        """Stage given files

        :param paths:
        :return:
        """
        return self._command.add_to_stage(paths)

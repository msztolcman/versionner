import importlib

from versionner.vcs import errors


class VCS:
    def __init__(self, engine):
        self._engine = engine

        try:
            builder = importlib.import_module('versionner.vcs.%s' % engine)
        except ImportError:
            raise errors.UnknownVCSError("Unknown VCS engine: %s" % engine)

        self._command = builder.VCSEngine()

    def create_tag(self, version, params):
        return self._command.create_tag(version, params)

    def raise_if_cant_commit(self):
        return self._command.raise_if_cant_commit()

    def create_commit(self, message):
        return self._command.create_commit(message)

    def add_to_stage(self, paths):
        return self._command.add_to_stage(paths)

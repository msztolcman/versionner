#!/usr/bin/env python

import os
from pathlib import Path
import re
import tempfile

import pytest

from versionner.cli import execute
from versionner.config import Config

from test.streamcatcher import catch_streams

def bootstrap_env():
    dir = tempfile.TemporaryDirectory()
    os.chdir(dir.name)

    execute('ver', ['init'])

    return dir


class TestDefault:
    @pytest.fixture(autouse=True)
    def set_dev(self):
        self.dir = bootstrap_env()
        self.root = Path(self.dir.name)
        self.cfg = Config()

    def test_empty(self):
        version = self.cfg.default_init_version
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', [])

        assert version_file.is_file(), "%s is not a file (exists: %s)" % (version_file, version_file.exists())

        with version_file.open('r') as fh:
            assert fh.read().strip() == version

    def test_not_initialized(self):
        version_file = self.root / self.cfg.version_file

        version_file.unlink()

        with catch_streams() as streams, \
                pytest.raises(SystemExit):
            execute('ver', [])

        assert re.search(r'(?ms).*Version file .* doesn\'t exists', streams.err.getvalue())

if __name__ == '__main__':
    pytest.main()

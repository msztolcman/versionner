#!/usr/bin/env python

import os
import tempfile
from pathlib import Path
import pytest
import re

from versionner.cli import execute
from versionner.config import Config
from versionner.version import Version

from test.streamcatcher import catch_streams


def bootstrap_env(create=True):
    dir = tempfile.TemporaryDirectory()
    os.chdir(dir.name)

    execute('ver', ['init'])

    return dir


class TestSet:
    @pytest.fixture(autouse=True)
    def set_env(self):
        self.dir = bootstrap_env()
        self.root = Path(self.dir.name)
        self.cfg = Config()

    def test_not_initialized(self):
        version = '1.2.3+asd'
        version_file = self.root / self.cfg.version_file

        version_file.unlink()

        with catch_streams() as streams,\
                pytest.raises(SystemExit):
            execute('ver', ['set', version])

        assert re.search(r'(?ms).*Version file .* doesn\'t exists', streams.err.getvalue())

    def test_without_version(self):
        with catch_streams() as streams, \
                pytest.raises(SystemExit):
            execute('ver', ['set'])

        assert re.search(r'Version is not specified', streams.err.getvalue())

    def test_specified_version(self):
        version = '1.2.3+asd'
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['set', version])

        assert version_file.is_file(), "%s is not a file (exists: %s)" % (version_file, version_file.exists())

        with version_file.open('r') as fh:
            assert fh.read().strip() == version

    def test_specified_fields(self):
        version = Version(self.cfg.default_init_version)
        version_file = self.root / self.cfg.version_file

        for field, value in zip(Version.VALID_FIELDS, (2, 3, 4, 'asd', 'qwe')):
            with catch_streams():
                execute('ver', ['set', '--%s' % field, str(value)])
            version = version.set(field, value)

            assert version_file.is_file(), "%s is not a file (exists: %s)" % (version_file, version_file.exists())

            with version_file.open('r') as fh:
                assert fh.read().strip() == str(version)

    def test_specified_fields_invalid(self):
        for field, value in zip(Version.VALID_UP_FIELDS, ('a', 'b', 'c')):
            with catch_streams() as streams,\
                    pytest.raises(SystemExit):
                execute('ver', ['set', '--%s' % field, str(value)])

            assert re.search(r'(?ms).*argument --%s.*invalid int value' % field, streams.err.getvalue())

        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        for field, value in zip(other_fields, ('ążśź', 'ążśź')):
            with catch_streams() as streams:
                execute('ver', ['set', '--%s' % field, str(value)])

            assert re.search(r'(?ms).*Invalid value for field %s: %s' % (field, value), streams.err.getvalue())
            streams.err.truncate()

    def test_all_fields_together(self):
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            args = ['set', '--major', '7', '--minor', '8', '--patch', '1', '--prerelease', 'ZZZ', '--build', 'XXX']
            execute('ver', args)

            assert version_file.is_file(), "%s is not a file (exists: %s)" % (version_file, version_file.exists())

            with version_file.open('r') as fh:
                assert fh.read().strip() == '7.8.1-ZZZ+XXX'

    def test_specified_invalid_version(self):
        version = '1.a.3+asd'

        with catch_streams() as streams:
            ret_code = execute('ver', ['set', version])

        assert ret_code == 2
        assert re.search(r'^InvalidVersionError:', streams.err.getvalue())


if __name__ == '__main__':
    pytest.main()

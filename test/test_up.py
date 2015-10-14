#!/usr/bin/env python

import os
import itertools
from pathlib import Path
import re
import tempfile

import pytest

from versionner.cli import execute
from versionner.config import Config
from versionner.version import Version

from test.streamcatcher import catch_streams


def bootstrap_env(create=True):
    dir = tempfile.TemporaryDirectory()
    os.chdir(dir.name)

    execute('ver', ['init'])

    return dir


class TestUp:
    @pytest.fixture(autouse=True)
    def set_env(self):
        self.dir = bootstrap_env()
        self.root = Path(self.dir.name)
        self.cfg = Config()

    def test_not_initialized(self):
        version_file = self.root / self.cfg.version_file

        version_file.unlink()

        with catch_streams() as streams,\
                pytest.raises(SystemExit):
            execute('ver', ['up'])

        assert re.search(r'(?ms).*Version file .* doesn\'t exists', streams.err.getvalue())

    def test_default_call(self):
        increase_value = self.cfg.default_increase_value
        version = Version(self.cfg.default_init_version)
        version_expected = version.up(self.cfg.up_part, increase_value)
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['up'])

        with version_file.open('r') as fh:
            assert fh.read().strip() == str(version_expected)

    def test_specified_increase_value(self):
        increase_value = 7
        version = Version(self.cfg.default_init_version)
        version_expected = version.up(self.cfg.up_part, increase_value)
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['up', str(increase_value)])

        with version_file.open('r') as fh:
            assert fh.read().strip() == str(version_expected)

    def test_specified_field_default_value(self):
        increase_value = self.cfg.default_increase_value
        version = Version(self.cfg.default_init_version)
        version_file = self.root / self.cfg.version_file

        for field in Version.VALID_UP_FIELDS:
            version = version.up(field, increase_value)

            with catch_streams():
                execute('ver', ['up', '--%s' % field])

            with version_file.open('r') as fh:
                assert fh.read().strip() == str(version)

        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        for field in other_fields:
            with pytest.raises(ValueError) as exc:
                version.up(field, increase_value)

            assert re.search(r'Invalid field type: %s' % field, str(exc.value))

    def test_specified_field_specified_value(self):
        increase_value = 7
        version = Version(self.cfg.default_init_version)
        version_file = self.root / self.cfg.version_file

        for field in Version.VALID_UP_FIELDS:
            version = version.up(field, increase_value)

            with catch_streams():
                execute('ver', ['up', '--%s' % field, str(increase_value)])

            with version_file.open('r') as fh:
                assert fh.read().strip() == str(version)

        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        for field in other_fields:
            with pytest.raises(ValueError) as exc:
                version.up(field, increase_value)

            assert re.search(r'Invalid field type: %s' % field, str(exc.value))

    def test_specified_invalid_field(self):
        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        other_fields.add('azsx')
        for field in other_fields:
            with catch_streams() as streams, \
                    pytest.raises(SystemExit):
                execute('ver', ['up', '--%s' % field])

            assert re.search(r'(?ms).*unrecognized arguments: --%s' % field, streams.err.getvalue())
            streams.err.truncate()

    def test_specified_field_invalid_value(self):
        increase_value = 'asd'
        for field in Version.VALID_UP_FIELDS:
            with catch_streams() as streams, \
                    pytest.raises(SystemExit):
                execute('ver', ['up', '--%s' % field, increase_value])

            assert re.search(r'(?ms).*argument value: invalid int value: \'%s\'' % increase_value, streams.err.getvalue())
            streams.err.truncate()

    def test_multiple_fields_together(self):
        for field1, field2 in itertools.permutations(('minor', 'major', 'patch'), 2):
            with catch_streams() as streams, \
                    pytest.raises(SystemExit):
                execute('ver', ['up', '--%s' % field1, '--%s' % field2])

            assert re.search(
                r'(?ms).*argument --(%s|%s)/-.: not allowed with argument --(%s|%s)/-.' % (
                    field1, field2, field1, field2
                ),
                streams.err.getvalue(),
            )
            streams.err.truncate()


if __name__ == '__main__':
    pytest.main()

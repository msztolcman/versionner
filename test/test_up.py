#!/usr/bin/env python

import os
import tempfile
import unittest
from pathlib import Path
import itertools

import semver

from versionner.cli import execute
from versionner.config import Config
from versionner.version import Version

from test.streamcatcher import catch_streams


def bootstrap_env(create=True):
    dir = tempfile.TemporaryDirectory()
    os.chdir(dir.name)

    execute('ver', ['init'])

    return dir


class UpTest(unittest.TestCase):
    def setUp(self):
        self.dir = bootstrap_env()
        self.root = Path(self.dir.name)
        self.cfg = Config()

    def test_not_initialized(self):
        version_file = self.root / self.cfg.version_file

        version_file.unlink()

        with catch_streams() as streams,\
                self.assertRaises(SystemExit):
            execute('ver', ['up'])

        self.assertRegex(streams.err.getvalue(), r'(?ms).*Version file .* doesn\'t exists')

    def test_default_call(self):
        increase_value = self.cfg.default_increase_value
        version = Version.from_str(self.cfg.default_init_version)
        version_expected = version.up(self.cfg.up_part, increase_value)
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['up'])

        with version_file.open('r') as fh:
            self.assertEqual(fh.read().strip(), str(version_expected))

    def test_specified_increase_value(self):
        increase_value = 7
        version = Version.from_str(self.cfg.default_init_version)
        version_expected = version.up(self.cfg.up_part, increase_value)
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['up', str(increase_value)])

        with version_file.open('r') as fh:
            self.assertEqual(fh.read().strip(), str(version_expected))

    def test_specified_field_default_value(self):
        increase_value = self.cfg.default_increase_value
        version = Version.from_str(self.cfg.default_init_version)
        version_file = self.root / self.cfg.version_file

        for field in Version.VALID_UP_FIELDS:
            version = version.up(field, increase_value)

            with catch_streams():
                execute('ver', ['up', '--%s' % field])

            with version_file.open('r') as fh:
                self.assertEqual(fh.read().strip(), str(version))

        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        for field in other_fields:
            with self.assertRaisesRegex(ValueError, r'Invalid field: %s' % field):
                version.up(field, increase_value)

    def test_specified_field_specified_value(self):
        increase_value = 7
        version = Version.from_str(self.cfg.default_init_version)
        version_file = self.root / self.cfg.version_file

        for field in Version.VALID_UP_FIELDS:
            version = version.up(field, increase_value)

            with catch_streams():
                execute('ver', ['up', '--%s' % field, str(increase_value)])

            with version_file.open('r') as fh:
                self.assertEqual(fh.read().strip(), str(version))

        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        for field in other_fields:
            with self.assertRaisesRegex(ValueError, r'Invalid field: %s' % field):
                version.up(field, increase_value)

    def test_specified_invalid_field(self):
        other_fields = set(Version.VALID_FIELDS) - set(Version.VALID_UP_FIELDS)
        other_fields.add('azsx')
        for field in other_fields:
            with catch_streams() as streams, \
                    self.assertRaises(SystemExit):
                execute('ver', ['up', '--%s' % field])

            self.assertRegex(streams.err.getvalue(), r'(?ms).*unrecognized arguments: --%s' % field)
            streams.err.truncate()

    def test_specified_field_invalid_value(self):
        increase_value = 'asd'
        for field in Version.VALID_UP_FIELDS:
            with catch_streams() as streams, \
                    self.assertRaises(SystemExit):
                execute('ver', ['up', '--%s' % field, increase_value])

            self.assertRegex(streams.err.getvalue(), r'(?ms).*argument value: invalid int value: \'%s\'' % increase_value)
            streams.err.truncate()

    def test_multiple_fields_together(self):
        for field1, field2 in itertools.permutations(('minor', 'major', 'patch'), 2):
            with catch_streams() as streams, \
                    self.assertRaises(SystemExit):
                execute('ver', ['up', '--%s' % field1, '--%s' % field2])

            self.assertRegex(
                streams.err.getvalue(),
                r'(?ms).*argument --(%s|%s)/-.: not allowed with argument --(%s|%s)/-.' % (
                    field1, field2, field1, field2
                )
            )
            streams.err.truncate()


if __name__ == '__main__':
    unittest.main()

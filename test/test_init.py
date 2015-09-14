#!/usr/bin/env python

import os
from pathlib import Path
import tempfile
import unittest

from versionner.cli import execute
from versionner.config import Config

from test.streamcatcher import catch_streams

def bootstrap_env():
    dir = tempfile.TemporaryDirectory()
    os.chdir(dir.name)

    return dir


class InitTest(unittest.TestCase):
    def setUp(self):
        self.dir = bootstrap_env()
        self.root = Path(self.dir.name)
        self.cfg = Config()

    def test_empty(self):
        version = self.cfg.default_init_version
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['init'])

        self.assertTrue(version_file.is_file(),
            "%s is not a file (exists: %s)" % (version_file, version_file.exists()))

        with version_file.open('r') as fh:
            self.assertEqual(fh.read().strip(), version)

    def test_specified_version(self):
        version = '1.2.3+asd'
        version_file = self.root / self.cfg.version_file

        with catch_streams():
            execute('ver', ['init', version])

        self.assertTrue(version_file.is_file(),
            "%s is not a file (exists: %s)" % (version_file, version_file.exists()))

        with version_file.open('r') as fh:
            self.assertEqual(fh.read().strip(), version)

    def test_specified_invalid_version(self):
        version = '1.a.3+asd'

        with catch_streams() as streams:
            ret_code = execute('ver', ['init', version])

        self.assertEqual(ret_code, 2)
        self.assertRegex(streams.err.getvalue(), r'^InvalidVersionError:')

    def test_version_file_exsists(self):
        version = '1.2.3+asd'
        version_file = self.root / self.cfg.version_file

        open(str(version_file), 'w').close()

        with catch_streams() as streams,\
                self.assertRaises(SystemExit):
            execute('ver', ['init', version])

        self.assertRegex(streams.err.getvalue(), r'Version file .* already exists')


if __name__ == '__main__':
    unittest.main()

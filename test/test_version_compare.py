#!/usr/bin/env python

import unittest

from versionner.version import Version


class VersionCompareTest(unittest.TestCase):
    def test_eq(self):
        v1 = Version.from_str('1.2.3')
        v2 = Version.from_str('2.3.4')
        v3 = Version.from_str('1.2.3')

        self.assertTrue(v1 == v3)
        self.assertFalse(v1 == v2)
        self.assertTrue(v1 == '1.2.3')
        self.assertFalse(v1 == '2.3.4')

    def test_lt(self):
        v1 = Version.from_str('1.2.3')
        v2 = Version.from_str('2.3.4')
        v3 = '7.6.5'

        self.assertTrue(v1 < v2)
        self.assertTrue(v1 < v3)
        self.assertTrue(v2 < v3)

    def test_gt(self):
        v1 = Version.from_str('1.2.3')
        v2 = Version.from_str('2.3.4')
        v3 = '7.6.5'

        self.assertTrue(v2 > v1)
        self.assertTrue(v3 > v1)
        self.assertTrue(v3 > v2)

    def test_sort(self):
        v1 = Version.from_str('1.2.3')
        v2 = Version.from_str('2.3.4')
        v3 = Version.from_str('1.2.3')
        v4 = '7.6.5'

        result = sorted([v1, v2, v3, v4])

        self.assertSequenceEqual(
            [id(o) for o in result],
            [id(v1), id(v3), id(v2), id(v4)]
        )


if __name__ == '__main__':
    unittest.main()

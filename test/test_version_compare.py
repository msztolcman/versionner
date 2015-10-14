#!/usr/bin/env python

import pytest

from versionner.version import Version


class TestVersionCompare:
    def test_eq(self):
        v1 = Version('1.2.3')
        v2 = Version('2.3.4')
        v3 = Version('1.2.3')

        assert v1 == v3
        assert v1 != v2
        assert v1 == '1.2.3'
        assert v1 != '2.3.4'

    def test_lt(self):
        v1 = Version('1.2.3')
        v2 = Version('2.3.4')
        v3 = '7.6.5'

        assert v1 < v2
        assert v1 < v3
        assert v2 < v3

    def test_gt(self):
        v1 = Version('1.2.3')
        v2 = Version('2.3.4')
        v3 = '7.6.5'

        assert v2 > v1
        assert v3 > v1
        assert v3 > v2

    def test_sort(self):
        v1 = Version('1.2.3')
        v2 = Version('2.3.4')
        v3 = Version('1.2.3')
        v4 = '7.6.5'

        result = sorted([v1, v2, v3, v4])

        assert [id(o) for o in result] == [id(v1), id(v3), id(v2), id(v4)]


if __name__ == '__main__':
    pytest.main()

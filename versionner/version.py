"""
    Playing with versions and version file
"""

import pathlib
import shutil
import tempfile
import functools
from collections import abc

import semver

from versionner.errors import InvalidVersionError


@functools.total_ordering
class Version:
    """
    Parse and manipulate version string
    """

    VALID_FIELDS = ('major', 'minor', 'patch', 'prerelease', 'build')
    VALID_UP_FIELDS = ('major', 'minor', 'patch')

    def __init__(self, version=None):
        """
        Initialise object

        :param version:Version object (to clone) or dictionary from semver.parse
        """

        if version is not None:
            self._parse(version)

    def _parse_object(self, version):
        self.major = version.major
        self.minor = version.minor
        self.patch = version.patch
        self.prerelease = getattr(version, 'prerelease', '')
        self.build = getattr(version, 'build', '')

    def _parse_dict(self, version):
        self.major = version['major']
        self.minor = version['minor']
        self.patch = version['patch']
        self.prerelease = version.get('prerelease', '')
        self.build = version.get('build', '')

    def _parse_str(self, version):
        version = semver.parse(version)
        self._parse_dict(version)

    def _parse(self, version):
        if all(hasattr(version, field) for field in self.VALID_UP_FIELDS):
            self._parse_object(version)
        elif isinstance(version, abc.Mapping):
            self._parse_dict(version)
        elif isinstance(version, (str, bytes)):
            if hasattr(version, 'decode'):
                version = version.decode()
            self._parse_str(version)
        else:
            raise InvalidVersionError("Unknown object type: %s" % type(version))

    # pylint: disable=invalid-name
    def up(self, field, value=None):
        """
        Increase version and return new instance

        :rtype : Version
        :param field:one of Version.VALID_UP_FIELDS
        :param value:int
        :return: :raise ValueError:
        """

        if field not in self.VALID_UP_FIELDS:
            raise ValueError("Invalid field: %s" % field)

        if not value:
            value = 1

        version = Version(self)

        if field == 'major':
            version.major += value
            version.minor = 0
            version.patch = 0
        elif field == 'minor':
            version.minor += value
            version.patch = 0
        else:
            version.patch += value

        return version

    def set(self, field, value):
        """
        Set any field of semver to `value`

        :rtype : Version
        :param field:type of field (one of Version.VALID_FIELDS)
        :param value:
        :return: :raise ValueError:
        """

        if field not in self.VALID_FIELDS:
            raise ValueError("Incorrect value of \"type\"")

        version = Version(self)
        setattr(version, field, value)

        semver.parse(str(version))

        return version

    def __str__(self):
        """
        Return version as string compatible with semver

        :return:str
        """

        return semver.format_version(self.major, self.minor, self.patch, self.prerelease or None, self.build or None)

    def __repr__(self):
        data = {field: getattr(self, field) for field in self.VALID_FIELDS}
        return ('<Version({major: %(major)s, minor: %(minor)s, patch: %(patch)s, '
               'prerelease: %(prerelease)s, build: %(build)s})>') % data

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            v1, v2 = str(self), str(other)
        elif isinstance(other, dict):
            v1, v2 = str(self), str(self.__class__(other))
        elif isinstance(other, str):
            v1, v2 = str(self), other
        else:
            return NotImplemented

        return semver.compare(v1, v2)

    def __eq__(self, other):
        result = self.__cmp__(other)
        if result is NotImplemented:
            return result

        return result == 0

    def __lt__(self, other):
        result = self.__cmp__(other)
        if result is NotImplemented:
            return result

        return result == -1

class VersionFile():
    """
    Manipulate project version file
    """

    def __init__(self, path):
        """
        Initialisation

        :param path:pathlib.Path
        """
        self._path = path

    def read(self):
        """
        Read version from version file

        :rtype : Version
        :return:
        """
        with self._path.open(mode='r') as fh:
            version = fh.read().strip()
            version = semver.parse(version)
            return Version(version)

    def write(self, version):
        """
        Save new version into self._path in safe way (using temporary file)

        :param version:Version
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fh:
            fh.write(str(version))

        if self._path.exists():
            shutil.copystat(str(self._path), fh.name)
        pathlib.Path(fh.name).rename(self._path)

    def __str__(self):
        return str(self._path)

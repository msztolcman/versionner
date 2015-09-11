"""
    Playing with versions and version file
"""

import pathlib
import shutil
import tempfile

import semver

class Version:
    """
    Parse and manipulate version string
    """

    VALID_FIELDS = ('major', 'minor', 'patch', 'prerelease', 'build')
    VALID_UP_FIELDS = ('major', 'minor', 'patch')

    def __init__(self, version_dict=None):
        """
        Initialise object

        :param version_dict:Version object (to clone) or dictionary from semver.parse
        """

        if isinstance(version_dict, Version):
            version_dict = {
                'major': version_dict.major,
                'minor': version_dict.minor,
                'patch': version_dict.patch,
                'prerelease': version_dict.prerelease,
                'build': version_dict.build,
            }

        self.major = version_dict['major']
        self.minor = version_dict['minor']
        self.patch = version_dict['patch']
        self.prerelease = version_dict.get('prerelease', '')
        self.build = version_dict.get('build', '')

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
            raise ValueError("Incorrect value of \"type\"")

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

        version = '.'.join([str(self.major), str(self.minor), str(self.patch)])
        if self.prerelease:
            version += '-' + str(self.prerelease)
        if self.build:
            version += '+' + str(self.build)

        return version


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

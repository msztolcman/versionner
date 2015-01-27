#!/usr/bin/env python

import argparse
import pathlib
import sys

import semver

"""
Versionner tool.
"""

__version__ = (pathlib.Path(__file__).parent / 'VERSION').open(mode="r").readline().strip()

class Version:
    """
    Version of project.
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

    def up(self, type, value=None):
        """
        Increase version and return new instance

        :rtype : Version
        :param type:one of Version.VALID_UP_FIELDS
        :param value:int
        :return: :raise ValueError:
        """

        if type not in self.VALID_UP_FIELDS:
            raise ValueError("Incorrect value of \"type\"")

        if not value:
            value = 1

        version = Version(self)

        if type == 'major':
            version.major += value
            version.minor = 0
            version.patch = 0
        elif type == 'minor':
            version.minor += value
            version.patch = 0
        else:
            version.patch += value

        return version

    def set(self, type, value):
        """
        Set any field of semver to `value`

        :rtype : Version
        :param type:type of field (one of Version.VALID_FIELDS)
        :param value:
        :return: :raise ValueError:
        """

        if type not in self.VALID_FIELDS:
            raise ValueError("Incorrect value of \"type\"")

        version = Version(self)
        setattr(version, type, value)

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
    Main file with projects version
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
        Save new version into file

        :param version:Version
        """
        with self._path.open(mode='w') as fh:
            fh.write(str(version))

    def __str__(self):
        return str(self._path)


def parse_args(args):
    """
    Parse input arguments of script.

    :rtype : argparse.Namespace
    :param args:
    :return:
    """
    prog = pathlib.Path(sys.argv[0]).parts[-1].replace('.py', '')
    version = "%%(prog)s %s" %__version__
    p = argparse.ArgumentParser(prog=prog, description='Manipulate version of project')
    p.add_argument('--file', '-f', type=str, default="./VERSION",
        help="path to file where version is saved")
    p.add_argument('--version', '-v', action="version", version=version)
    # p.add_argument('--git', '-g', action="store_true", help="")

    sub = p.add_subparsers()

    p_init = sub.add_parser('init',
        help="Create new version file")
    p_init.add_argument('value', nargs='?', default='0.1.0', type=str,
        help="Initial version")

    p_up = sub.add_parser('up',
        help="Increase version")
    p_up.add_argument('value', nargs='?', type=int,
        help="Increase version by this value (default: 1)")

    p_up_gr = p_up.add_mutually_exclusive_group()
    p_up_gr.add_argument('--major', '-j', action="store_true",
        help="increase major part of version")
    p_up_gr.add_argument('--minor', '-n', action="store_true",
        help="increase minor part of version (default)")
    p_up_gr.add_argument('--patch', '-p', action="store_true",
        help="increase patch part of version")

    p_set = sub.add_parser('set',
        help="Set version to specified one")
    p_set.add_argument('--major', '-j', type=int,
        help="set major part of version to MAJOR")
    p_set.add_argument('--minor', '-n', type=int,
        help="set minor part of version to MINOR")
    p_set.add_argument('--patch', '-p', type=int,
        help="set patch part of version to PATCH")
    p_set.add_argument('--prerelease', '-r', type=str,
        help="set prerelease part of version to PRERELEASE")
    p_set.add_argument('--build', '-b', type=str,
        help="set build part of version to BUILD")
    p_set.add_argument('value', nargs='?', type=str,
        help="set version to this value")

    args = p.parse_args(args)
    args.file = pathlib.Path(args.file).absolute()

    ## TODO: how can I do that better?
    if hasattr(args, 'build'):
        args.command = 'set'
    elif hasattr(args, 'major'):
        args.command = 'up'
    elif hasattr(args, 'value'):
        args.command = 'init'
        if args.file.exists():
            p.error("Version file \"%s\" already exists" % args.file)
    else:
        args.command = None

    return args


def main(args):
    """
    Main script

    :param args:
    :return:
    """

    args = parse_args(args)

    file = VersionFile(args.file)
    if args.command == 'up':
        current = file.read()
        if args.major:
            new = current.up('major', args.value)
        elif args.patch:
            new = current.up('patch', args.value)
        else:
            new = current.up('minor', args.value)
        file.write(new)
        current = new

    elif args.command == 'set':
        current = file.read()
        if args.value:
            parsed = semver.parse(args.value)
            new = Version(parsed)
        else:
            new = Version(current)
            for type_ in Version.VALID_FIELDS:
                value = getattr(args, type_)
                if value:
                    new = new.set(type_, value)

        file.write(new)
        current = new

    elif args.command == 'init':
        parsed = semver.parse(args.value)
        current = Version(parsed)
        file.write(current)
    else:
        current = file.read()

    print("Current version: %s" % current)


if __name__ == '__main__':
    main(sys.argv[1:])

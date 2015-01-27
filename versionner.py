#!/usr/bin/env python

import argparse
import pathlib
import sys

import semver


class Version:
    VALID_FIELDS = ('major', 'minor', 'patch', 'prerelease', 'build')
    VALID_UP_FIELDS = ('major', 'minor', 'patch')

    def __init__(self, version_dict=None):
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
        if type not in self.VALID_FIELDS:
            raise ValueError("Incorrect value of \"type\"")

        version = Version(self)
        setattr(version, type, value)

        semver.parse(str(version))

        return version

    def __str__(self):
        version = '.'.join([str(self.major), str(self.minor), str(self.patch)])
        if self.prerelease:
            version += '-' + str(self.prerelease)
        if self.build:
            version += '+' + str(self.build)

        return version


class VersionFile():
    def __init__(self, path):
        self._path = path

    def read(self):
        with self._path.open(mode='r') as fh:
            version = fh.read().strip()
            version = semver.parse(version)
            return Version(version)

    def write(self, version):
        with self._path.open(mode='w') as fh:
            fh.write(str(version))

    def __str__(self):
        return str(self._path)


def parse_args(args):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--file', '-f', type=str, default="./VERSION", help="")
    # p.add_argument('--git', '-g', action="store_true", help="")

    sub = p.add_subparsers()

    p_up = sub.add_parser('up')
    p_up.add_argument('value', nargs='?', type=int, help="")

    p_up_gr = p_up.add_mutually_exclusive_group()
    p_up_gr.add_argument('--major', '-j', action="store_true", help="")
    p_up_gr.add_argument('--minor', '-n', action="store_true", help="")
    p_up_gr.add_argument('--patch', '-p', action="store_true", help="")

    p_set = sub.add_parser('set')
    p_set.add_argument('--major', '-j', type=int, help="")
    p_set.add_argument('--minor', '-n', type=int, help="")
    p_set.add_argument('--patch', '-p', type=int, help="")
    p_set.add_argument('--prerelease', '-r', type=str, help="")
    p_set.add_argument('--build', '-b', type=str, help="")
    p_set.add_argument('value', nargs='?', type=str, help="")

    args = p.parse_args(args)
    args.file = pathlib.Path(args.file).absolute()

    ## TODO: how can I do that better?
    if hasattr(args, 'build'):
        args.command = 'set'
    elif hasattr(args, 'major'):
        args.command = 'up'
    else:
        args.command = None

    return args


def main():
    args = parse_args(sys.argv[1:])

    file = VersionFile(args.file)
    current = file.read()
    if args.command == 'up':
        if args.major:
            new = current.up('major', args.value)
        elif args.patch:
            new = current.up('patch', args.value)
        else:
            new = current.up('minor', args.value)
        file.write(new)
        current = new

    elif args.command == 'set':
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

    print("Current version: %s" % current)


if __name__ == '__main__':
    main()

#!/usr/bin/env python

import argparse
import pathlib
import sys

import semver


class Version:
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
        if type not in ('major', 'minor', 'patch'):
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
        if type not in ('major', 'minor', 'patch', 'prerelease', 'build'):
            raise ValueError("Incorrect value of \"type\"")

        version = Version(self)
        setattr(version, type, value)

        return version

    def __str__(self):
        version = '.'.join([str(self.major), str(self.minor), str(self.patch)])
        if self.prerelease:
            version += '-' + str(self.prerelease)
        if self.build:
            version += '+' + str(self.build)

        return version


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
    p_set.add_argument('--major', '-j', type=str, help="")
    p_set.add_argument('--minor', '-n', type=str, help="")
    p_set.add_argument('--patch', '-p', type=str, help="")
    p_set.add_argument('--prerelease', '-r', type=str, help="")
    p_set.add_argument('--build', '-b', type=str, help="")

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


def read_current_version(path):
    with path.open(mode='r') as fh:
        version = fh.read().strip();
        version = semver.parse(version)
        return Version(version)


def write_version(path, version):
    with path.open(mode='w') as fh:
        fh.write(str(version))


def main():
    args = parse_args(sys.argv[1:])

    current = read_current_version(args.file)
    if not args.command:
        print(current)
        sys.exit(0)
    elif args.command == 'up':
        if args.major:
            new = current.up('major', args.value)
        elif args.patch:
            new = current.up('patch', args.value)
        else:
            new = current.up('minor', args.value)
        write_version(args.file, new)
    elif args.command == 'set':
        new = Version(current)
        for type_ in ('major', 'minor', 'patch', 'prerelease', 'build'):
            value = getattr(args, type_)
            if value:
                new = new.set(type_, value)
        write_version(args.file, new)

if __name__ == '__main__':
    main()

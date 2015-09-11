"""
    Main CLI engine for versionner
    Parse input options, and make all dirty jobs.
"""

from versionner import utils

utils.validate_python_version()

import argparse
import pathlib
import re
import shutil
import sys
import tempfile
import time
import traceback

import semver

import versionner
from versionner import config
from versionner import version
from versionner import vcs


def parse_args(args, **defaults):
    """
    Parse input arguments of script.

    :rtype : argparse.Namespace
    :param args:
    :return:
    """
    prog = pathlib.Path(sys.argv[0]).parts[-1].replace('.py', '')
    prog_version = "%%(prog)s %s" % versionner.__version__

    # pylint: disable=invalid-name
    p = argparse.ArgumentParser(prog=prog, description='Helps manipulating version of the project')
    p.add_argument('--file', '-f', dest='version_file', type=str,
        default=defaults.get('version_file'),
        help="path to file where version is saved")
    p.add_argument('--version', '-v', action="version", version=prog_version)
    p.add_argument('--date-format', type=str,
        default=defaults.get('date_format'),
        help="Date format used in project files")
    p.add_argument('--vcs-engine', type=str,
        default=defaults.get('vcs_engine'),
        help="Select VCS engine (only git is supported currently)", )
    p.add_argument('--vcs-commit-message', '-m', type=str,
        default=defaults.get('vcs_commit_message'),
        help="Commit message used when committing changes")
    p.add_argument('--verbose', action="store_true",
        help="Be more verbose if it's possible")

    def get_command_name(name):
        # pylint: disable=missing-docstring
        _name = name

        def _():
            # pylint: disable=missing-docstring
            return _name

        return _

    sub = p.add_subparsers()

    p_init = sub.add_parser('init',
        help="Create new version file")
    p_init.add_argument('value', nargs='?', type=str,
        default=defaults.get('default_init_version'),
        help="Initial version")
    p_init.add_argument('--commit', '-c', action='store_true',
        help="Commit changes done by `up` command (only if there is no changes in repo before)")
    p_init.set_defaults(get_command=get_command_name('init'))

    p_up = sub.add_parser('up',
        help="Increase version")
    p_up.add_argument('--commit', '-c', action='store_true',
        help="Commit changes done by `up` command (only if there is no changes in repo before)")
    p_up.add_argument('value', nargs='?', type=int,
        help="Increase version by this value (default: 1)")
    p_up.set_defaults(get_command=get_command_name('up'))

    p_up_gr = p_up.add_mutually_exclusive_group()
    up_part = defaults.get('up_part')
    p_up_gr.add_argument('--major', '-j', action="store_true",
        help="increase major part of version" + (" (project default)" if up_part == 'major' else ""))
    p_up_gr.add_argument('--minor', '-n', action="store_true",
        help="increase minor part of version" + (" (project default)" if up_part == 'minor' else ""))
    p_up_gr.add_argument('--patch', '-p', action="store_true",
        help="increase patch part of version" + (" (project default)" if up_part == 'patch' else ""))
    p_up_gr.set_defaults(get_command=get_command_name('up'))

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
    p_set.add_argument('--commit', '-c', action='store_true',
        help="Commit changes done by `set` command (only if there is no changes in repo before)")
    p_set.add_argument('value', nargs='?', type=str,
        help="set version to this value")
    p_set.set_defaults(get_command=get_command_name('set'))

    p_tag = sub.add_parser('tag',
        help="Create VCS tag with current version")
    p_tag.add_argument('--vcs-tag-param', dest='vcs_tag_params', type=str, action="append",
        help="Additional params for VCS for \"tag\" command")
    p_tag.set_defaults(get_command=get_command_name('tag'))

    args = p.parse_args(args)
    args.version_file = pathlib.Path(args.version_file).absolute()

    if not hasattr(args, 'get_command'):
        args.get_command = get_command_name(None)

    if args.get_command() in ('up', 'set'):
        if not args.version_file.exists():
            p.error("Version file \"%s\" doesn't exists" % args.version_file)

    elif args.get_command() == 'init':
        if args.version_file.exists():
            p.error("Version file \"%s\" already exists" % args.version_file)

    elif args.get_command() == 'tag':
        if not args.vcs_tag_params:
            args.vcs_tag_params = defaults.get('vcs_tag_params', [])

    return args


def update_project_files(args, cfg, proj_version):
    """
    Update version string in project files

    :rtype : dict
    :param args:script arguments
    :param cfg:project configuration
    :param proj_version:current version
    :return:dict :raise ValueError:
    """
    counters = {'files': 0, 'changes': 0}

    for project_file in cfg.files:
        if not project_file.file.exists():
            print("File \"%s\" not found" % project_file.filename, file=sys.stderr)
            continue

        # prepare data
        date_format = project_file.date_format or args.date_format

        rxp = re.compile(project_file.search, project_file.search_flags)
        replace = project_file.replace % {
            "date": time.strftime(date_format),
            "major": proj_version.major,
            "minor": proj_version.minor,
            "patch": proj_version.patch,
            "prerelease": proj_version.prerelease,
            "version": str(proj_version),
            "build": proj_version.build,
        }

        # update project files
        with \
                project_file.file.open(mode="r", encoding=project_file.encoding) as fh_in, \
                tempfile.NamedTemporaryFile(mode="w", encoding=project_file.encoding, delete=False) as fh_out:
            if project_file.match == 'line':
                changes = 0
                for line in fh_in:
                    (line, cnt) = rxp.subn(replace, line)
                    if cnt:
                        changes += cnt
                    fh_out.write(line)

                if changes:
                    counters['files'] += 1
                    counters['changes'] += changes

            elif project_file.match == 'file':
                data = fh_in.read()
                (data, cnt) = rxp.subn(replace, data)
                if cnt:
                    counters['files'] += 1
                    counters['changes'] += cnt
                fh_out.write(data)

            else:
                raise ValueError("Unknown match type: \"%s\"" % project_file.match)

            fh_out.close()

            shutil.copystat(project_file.filename, fh_out.name)
            pathlib.Path(fh_out.name).rename(project_file.filename)

    return counters


def command_up(cfg, args):
    """
    Realize tasks for 'up' command

    :param cfg:
    :param args:
    :return:
    """

    vcs_handler = None
    if args.commit:
        vcs_handler = vcs.VCS(args.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(args.version_file)

    current = version_file.read()

    if args.major:
        new = current.up('major', args.value)
    elif args.minor:
        new = current.up('minor', args.value)
    elif args.patch:
        new = current.up('patch', args.value)
    else:
        new = current.up(cfg.up_part, args.value)

    version_file.write(new)
    current = new

    quant = update_project_files(args, cfg, current)

    if args.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(cfg.version_file)
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(args.vcs_commit_message % current)

    return {'current_version': current, 'quant': quant, 'commit': args.commit}


def command_set(cfg, args):
    """
    Realize tasks for 'set' command

    :param cfg:
    :param args:
    :return:
    """

    vcs_handler = None
    if args.commit:
        vcs_handler = vcs.VCS(args.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(args.version_file)

    current = version_file.read()

    if args.value:
        parsed = semver.parse(args.value)
        new = version.Version(parsed)
    else:
        new = version.Version(current)
        for type_ in version.Version.VALID_FIELDS:
            value = getattr(args, type_)
            if value:
                new = new.set(type_, value)

    version_file.write(new)
    current = new

    quant = update_project_files(args, cfg, current)

    if args.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(cfg.version_file)
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(args.vcs_commit_message % current)

    return {'current_version': current, 'quant': quant, 'commit': args.commit}


# pylint: disable=unused-argument
def command_init(cfg, args):
    """
    Realize tasks for 'init' command

    :param cfg:
    :param args:
    :return:
    """

    vcs_handler = None
    if args.commit:
        vcs_handler = vcs.VCS(args.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(args.version_file)

    parsed = semver.parse(args.value)
    current = version.Version(parsed)
    version_file.write(current)

    if args.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(cfg.version_file)
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(args.vcs_commit_message % current)

    return {'current_version': current, 'quant': 0, 'commit': args.commit}


# pylint: disable=unused-argument
def command_tag(cfg, args):
    """
    Realize tasks for 'tag' command

    :param cfg:
    :param args:
    :return:
    """
    version_file = version.VersionFile(args.version_file)

    try:
        current = version_file.read()
        vcs_handler = vcs.VCS(args.vcs_engine)
        vcs_handler.create_tag(current, args.vcs_tag_params)
    # pylint: disable=bare-except
    except:
        print('Git tag failed, do it yourself')
        if args.verbose:
            traceback.print_exc()
    else:
        print('Git tag created')

    return {'current_version': current, 'quant': 0}


# pylint: disable=unused-argument
def command_default(cfg, args):
    """
    Realize tasks when no command given

    :param cfg:
    :param args:
    :return:
    """
    version_file = version.VersionFile(args.version_file)

    current = version_file.read()

    return {'current_version': current, 'quant': 0}


def main():
    """
    Main script

    :return:
    """

    if pathlib.Path(sys.argv[0]).parts[-1] in ('versionner', 'versionner.py'):
        print("versionner name is deprecated, use \"ver\" now!", file=sys.stderr)

    project_cfg = config.Config()
    args = parse_args(sys.argv[1:], version_file=project_cfg.version_file, date_format=project_cfg.date_format,
        up_part=project_cfg.up_part, vcs_engine=project_cfg.vcs_engine, vcs_tag_params=project_cfg.vcs_tag_params,
        default_init_version=project_cfg.default_init_version, vcs_commit_message=project_cfg.vcs_commit_message)

    commands = {'up': command_up, 'set': command_set, 'init': command_init, 'tag': command_tag}
    result = commands.get(args.get_command(), command_default)(project_cfg, args)
    quant = result['quant']
    current = result['current_version']
    commit = result.get('commit')

    print("Current version: %s" % current)

    if quant:
        print('Changed' + (' and committed' if commit else '') + ' %(files)s files (%(changes)s changes)' % quant)

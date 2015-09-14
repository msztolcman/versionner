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
# pylint: disable=wildcard-import
from versionner.errors import *

# pylint: disable=too-many-branches,too-many-statements
def parse_args(args, cfg):
    """
    Parse input arguments of script.

    :rtype : argparse.Namespace
    :param args:
    :rtype : Config
    :param cfg:
    :return:
    """
    prog = pathlib.Path(sys.argv[0]).parts[-1].replace('.py', '')
    prog_version = "%%(prog)s %s" % versionner.__version__

    # pylint: disable=invalid-name
    p = argparse.ArgumentParser(prog=prog, description='Helps manipulating version of the project')
    p.add_argument('--file', '-f', dest='version_file', type=str,
        default=cfg.version_file,
        help="path to file where version is saved")
    p.add_argument('--version', '-v', action="version", version=prog_version)
    p.add_argument('--date-format', type=str,
        default=cfg.date_format,
        help="Date format used in project files")
    p.add_argument('--verbose', action="store_true",
        help="Be more verbose if it's possible")

    def get_command_name(name):
        # pylint: disable=missing-docstring
        return lambda: name

    sub = p.add_subparsers()

    p_init = sub.add_parser('init',
        help="Create new version file")
    p_init.add_argument('value', nargs='?', type=str,
        default=cfg.default_init_version,
        help="Initial version")
    p_init.add_argument('--vcs-engine', type=str,
        default=cfg.vcs_engine,
        help="Select VCS engine (only git is supported currently)", )
    p_init.add_argument('--vcs-commit-message', '-m', type=str,
        default=cfg.vcs_commit_message,
        help="Commit message used when committing changes")
    p_init.add_argument('--commit', '-c', action='store_true',
        help="Commit changes done by `up` command (only if there is no changes in repo before)")
    p_init.set_defaults(get_command=get_command_name('init'))

    p_up = sub.add_parser('up',
        help="Increase version")
    p_up.add_argument('--vcs-engine', type=str,
        default=cfg.vcs_engine,
        help="Select VCS engine (only git is supported currently)", )
    p_up.add_argument('--vcs-commit-message', '-m', type=str,
        default=cfg.vcs_commit_message,
        help="Commit message used when committing changes")
    p_up.add_argument('--commit', '-c', action='store_true',
        help="Commit changes done by `up` command (only if there is no changes in repo before)")
    p_up.add_argument('value', nargs='?', type=int,
        default=cfg.default_increase_value,
        help="Increase version by this value (default: %d)" % cfg.default_increase_value)

    p_up.set_defaults(get_command=get_command_name('up'))

    p_up_gr = p_up.add_mutually_exclusive_group()
    p_up_gr.add_argument('--major', '-j', action="store_true",
        help="increase major part of version" + (" (project default)" if cfg.up_part == 'major' else ""))
    p_up_gr.add_argument('--minor', '-n', action="store_true",
        help="increase minor part of version" + (" (project default)" if cfg.up_part == 'minor' else ""))
    p_up_gr.add_argument('--patch', '-p', action="store_true",
        help="increase patch part of version" + (" (project default)" if cfg.up_part == 'patch' else ""))
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
    p_set.add_argument('--vcs-engine', type=str,
        default=cfg.vcs_engine,
        help="Select VCS engine (only git is supported currently)", )
    p_set.add_argument('--vcs-commit-message', '-m', type=str,
        default=cfg.vcs_commit_message,
        help="Commit message used when committing changes")
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

    if not hasattr(args, 'get_command'):
        args.get_command = get_command_name(None)

    cfg.command = args.get_command()
    cfg.version_file = pathlib.Path(args.version_file).absolute()
    cfg.date_format = args.date_format
    cfg.verbose = args.verbose

    version_file_requirement = 'doesn\'t matter'
    if cfg.command == 'init':
        version_file_requirement = 'none'

        cfg.commit = args.commit
        cfg.vcs_engine = args.vcs_engine
        cfg.vcs_commit_message = args.vcs_commit_message
        cfg.value = args.value

    elif cfg.command == 'up':
        version_file_requirement = 'required'

        cfg.commit = args.commit
        cfg.vcs_engine = args.vcs_engine
        cfg.vcs_commit_message = args.vcs_commit_message
        cfg.value = args.value
        if args.major:
            cfg.up_part = 'major'
        elif args.minor:
            cfg.up_part = 'minor'
        elif args.patch:
            cfg.up_part = 'patch'

    elif cfg.command == 'set':
        version_file_requirement = 'required'

        cfg.commit = args.commit
        cfg.vcs_engine = args.vcs_engine
        cfg.vcs_commit_message = args.vcs_commit_message

        if args.value:
            cfg.value = args.value
        else:
            cfg.value = (
                args.major, args.minor, args.patch,
                args.prerelease, args.build
            )

            if all(value is None for value in cfg.value):
                p.error("Version is not specified")

    elif cfg.command == 'tag':
        version_file_requirement = 'required'

        cfg.vcs_tag_params = args.vcs_tag_params or []

    elif cfg.command is None:
        version_file_requirement = 'required'

    if version_file_requirement == 'required':
        if not cfg.version_file.exists():
            p.error("Version file \"%s\" doesn't exists" % cfg.version_file)
    elif version_file_requirement == 'none':
        if cfg.version_file.exists():
            p.error("Version file \"%s\" already exists" % cfg.version_file)


def update_project_files(cfg, proj_version):
    """
    Update version string in project files

    :rtype : dict
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
        date_format = project_file.date_format or cfg.date_format

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
                raise ConfigError("Unknown match type: \"%s\"" % project_file.match)

            fh_out.close()

            shutil.copystat(project_file.filename, fh_out.name)
            pathlib.Path(fh_out.name).rename(project_file.filename)

    return counters


def command_up(cfg):
    """
    Realize tasks for 'up' command

    :param cfg:
    :return:
    """

    vcs_handler = None
    if cfg.commit:
        vcs_handler = vcs.VCS(cfg.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(cfg.version_file)

    current = version_file.read()

    new = current.up(cfg.up_part, cfg.value)

    version_file.write(new)
    current = new

    quant = update_project_files(cfg, current)

    if cfg.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(str(cfg.version_file))
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(cfg.vcs_commit_message % current)

    return {'current_version': current, 'quant': quant, 'commit': cfg.commit}


def command_set(cfg):
    """
    Realize tasks for 'set' command

    :param cfg:
    :return:
    """

    vcs_handler = None
    if cfg.commit:
        vcs_handler = vcs.VCS(cfg.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(cfg.version_file)

    current = version_file.read()

    if isinstance(cfg.value, tuple):
        new = version.Version(current)

        try:
            for field, value in zip(version.Version.VALID_FIELDS, cfg.value):
                if value is not None:
                    new = new.set(field, value)
        except ValueError as exc:
            raise InvalidVersionError("Cannot use \"%s\" as \"--%s\" field" % (value, field)) from exc
    else:
        try:
            parsed = semver.parse(cfg.value)
        except ValueError as exc:
            raise InvalidVersionError("Cannot parse version string: %s" % cfg.value) from exc

        new = version.Version(parsed)

    version_file.write(new)
    current = new

    quant = update_project_files(cfg, current)

    if cfg.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(str(cfg.version_file))
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(cfg.vcs_commit_message % current)

    return {'current_version': current, 'quant': quant, 'commit': cfg.commit}


def command_init(cfg):
    """
    Realize tasks for 'init' command

    :rtype : Config :
    :param cfg:
    :return:
    """

    vcs_handler = None
    if cfg.commit:
        vcs_handler = vcs.VCS(cfg.vcs_engine)
        vcs_handler.raise_if_cant_commit()

    version_file = version.VersionFile(cfg.version_file)

    try:
        parsed = semver.parse(cfg.value)
    except ValueError as exc:
        raise InvalidVersionError("Cannot parse version string: %s" % cfg.value) from exc

    current = version.Version(parsed)
    version_file.write(current)

    if cfg.commit:
        files = {str(file.file) for file in cfg.files}
        files.add(str(cfg.version_file))
        vcs_handler.add_to_stage(files)
        vcs_handler.create_commit(cfg.vcs_commit_message % current)

    return {'current_version': current, 'quant': 0, 'commit': cfg.commit}


def command_tag(cfg):
    """
    Realize tasks for 'tag' command

    :param cfg:
    :return:
    """
    version_file = version.VersionFile(cfg.version_file)

    current = version_file.read()
    try:
        vcs_handler = vcs.VCS(cfg.vcs_engine)
        vcs_handler.create_tag(current, cfg.vcs_tag_params)
    # pylint: disable=bare-except
    except:
        print('Git tag failed, do it yourself')
        if cfg.verbose:
            traceback.print_exc()
    else:
        print('Git tag created')

    return {'current_version': current, 'quant': 0}


# pylint: disable=unused-argument
def command_default(cfg):
    """
    Realize tasks when no command given

    :param cfg:
    :return:
    """
    version_file = version.VersionFile(cfg.version_file)

    current = version_file.read()

    return {'current_version': current, 'quant': 0}


def execute(prog, argv):
    """
    Execute whole program

    :param prog: program name
    :param argv: list: script arguments
    :return:
    """
    if pathlib.Path(prog).parts[-1] in ('versionner', 'versionner.py'):
        print("versionner name is deprecated, use \"ver\" now!", file=sys.stderr)

    cfg = config.Config()
    parse_args(argv, cfg)

    commands = {'up': command_up, 'set': command_set, 'init': command_init, 'tag': command_tag}

    try:
        result = commands.get(cfg.command, command_default)(cfg)
    except VersionnerError as exc:
        print('%s: %s' % (exc.__class__.__name__, exc), file=sys.stderr)
        return exc.ret_code

    quant = result['quant']
    current = result['current_version']
    commit = result.get('commit')

    print("Current version: %s" % current)

    if quant:
        print('Changed' + (' and committed' if commit else '') + ' %(files)s files (%(changes)s changes)' % quant)

    return 0

def main():
    """
    Main script

    :return:
    """

    return execute(sys.argv[0], sys.argv[1:])

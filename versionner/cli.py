"""
    Main CLI engine for versionner
    Parse input options, and make all dirty jobs.
"""

from versionner import utils

utils.validate_python_version()

import argparse
import pathlib
import os.path
import re
import shutil
import sys
import tempfile
import time

import versionner
from versionner import config
from versionner import defaults
from versionner import vcs
from versionner import commands

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

    sub = p.add_subparsers(dest='command')

    p_init = sub.add_parser('init', aliases=commands.get_aliases_for('init'),
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

    p_up = sub.add_parser('up', aliases=commands.get_aliases_for('up'),
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

    p_up_gr = p_up.add_mutually_exclusive_group()
    p_up_gr.add_argument('--major', '-j', action="store_true",
        help="increase major part of version" + (" (project default)" if cfg.up_part == 'major' else ""))
    p_up_gr.add_argument('--minor', '-n', action="store_true",
        help="increase minor part of version" + (" (project default)" if cfg.up_part == 'minor' else ""))
    p_up_gr.add_argument('--patch', '-p', action="store_true",
        help="increase patch part of version" + (" (project default)" if cfg.up_part == 'patch' else ""))

    p_set = sub.add_parser('set', aliases=commands.get_aliases_for('set'),
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

    p_tag = sub.add_parser('tag', aliases=commands.get_aliases_for('tag'),
        help="Create VCS tag with current version")
    p_tag.add_argument('--vcs-tag-param', dest='vcs_tag_params', type=str, action="append",
        help="Additional params for VCS for \"tag\" command")

    p_read = sub.add_parser('read', aliases=commands.get_aliases_for('read'),
        help="Read current version")

    args = p.parse_args(args)

    cfg.command = args.command
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
        cfg.command = 'read'
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


def save_version_and_update_files(cfg, version_file, version_to_save):
    """
    Save version to version_file and commit changes if required

    :param cfg:
    :param version_file:
    :param version_to_save:
    :return:
    """
    with vcs.VCS(cfg.vcs_engine) as vcs_handler:
        if cfg.commit:
            vcs_handler.raise_if_cant_commit()

        version_file.write(version_to_save)

        quant = update_project_files(cfg, version_to_save)

        if cfg.commit:
            files = {str(file.file) for file in cfg.files}
            files.add(str(cfg.version_file))
            vcs_handler.add_to_stage(files)
            vcs_handler.create_commit(cfg.vcs_commit_message % {'version': version_to_save})

    return quant


def _find_project_config_file(user_config_file):
    """
    Find path to project-wide config file
    Search from current working directory, and traverse path up to
    directory with .versionner.rc file or root directory

    :param user_config_file:pathlib.Path instance with user-wide config path
    :return:pathlib.Path
    """
    proj_cfg_dir = pathlib.Path('.').absolute()
    proj_cfg_file = None
    root = pathlib.Path('/')
    while proj_cfg_dir != root:
        proj_cfg_file = proj_cfg_dir / defaults.RC_FILENAME
        if proj_cfg_file.exists():
            break

        proj_cfg_file = None
        proj_cfg_dir = proj_cfg_dir.parent

    if proj_cfg_file and proj_cfg_file != user_config_file:
        return proj_cfg_file


def execute(prog, argv):
    """
    Execute whole program

    :param prog: program name
    :param argv: list: script arguments
    :return:
    """
    if pathlib.Path(prog).parts[-1] in ('versionner', 'versionner.py'):
        print("versionner name is deprecated, use \"ver\" now!", file=sys.stderr)

    cfg_files = [
        pathlib.Path(os.path.expanduser('~')) / defaults.RC_FILENAME,
    ]
    proj_cfg_file = _find_project_config_file(cfg_files[0])
    if proj_cfg_file:
        cfg_files.append(proj_cfg_file)

    cfg = config.Config(cfg_files)
    parse_args(argv, cfg)

    cmd = commands.get(cfg.command, cfg)

    try:
        result = cmd.execute()
    except VersionnerError as exc:
        print('%s: %s' % (exc.__class__.__name__, exc), file=sys.stderr)
        return exc.ret_code

    print("Current version: %s" % (result.current_version, ))

    if result.modified_files:
        print('Changed' + (' and committed' if cfg.commit else '') + ' %(files)s files (%(changes)s changes)' % {
            'files': result.modified_files,
            'changes': result.changes,
        })

    return 0

def main():
    """
    Main script

    :return:
    """

    return execute(sys.argv[0], sys.argv[1:])

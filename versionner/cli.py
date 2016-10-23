"""Main CLI engine for versionner
Parse input options, and make all dirty jobs.
"""

# pylint: disable=wrong-import-position
from versionner import utils

utils.validate_python_version()

# pylint: disable=wrong-import-order
import argparse
import pathlib
import os.path
import sys

import versionner
from versionner import config
from versionner import defaults
from versionner import commands
from versionner.errors import VersionnerError


# pylint: disable=too-many-branches,too-many-statements
def parse_args(args, cfg):
    """Parse input arguments of script.

    :param args: list of parameters
    :type: argparse.Namespace
    :param cfg: configuration storage
    :type: Config
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

    sub.add_parser('read', aliases=commands.get_aliases_for('read'),
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


def _find_project_config_file(user_config_file):
    """Find path to project-wide config file
    Search from current working directory, and traverse path up to
    directory with .versionner.rc file or root directory

    :param user_config_file: instance with user-wide config path
    :type: pathlib.Path
    :rtype: pathlib.Path
    """
    proj_cfg_dir = pathlib.Path('.').absolute()
    proj_cfg_file = None
    root = pathlib.Path('/')
    while proj_cfg_dir != root:
        proj_cfg_file = proj_cfg_dir / defaults.RC_FILENAME
        if proj_cfg_file.exists():
            break

        proj_cfg_file = None
        # pylint: disable=redefined-variable-type
        proj_cfg_dir = proj_cfg_dir.parent

    if proj_cfg_file and proj_cfg_file != user_config_file:
        return proj_cfg_file


def execute(prog, argv):
    """Execute whole program

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
            'changes': result.modifications,
        })

    return 0

def main():
    """Main script

    :return: exit code (for shell)
    :rtype: int
    """

    return execute(sys.argv[0], sys.argv[1:])

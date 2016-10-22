"""Helpers for commands related to manipulating files"""

import pathlib
import re
import shutil
import sys
import tempfile
import time

from versionner import vcs
from versionner.errors import ConfigError


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
    """Save version to version_file and commit changes if required

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

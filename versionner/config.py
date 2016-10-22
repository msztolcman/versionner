"""Configuration-related classes for versionner"""

import codecs
import configparser
import pathlib
import re
import sys

from versionner import defaults


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class FileConfig:
    """Single project file configuration"""

    def __init__(self, filename, cfg):
        """
        Evaluate single file configuration

        :param filename:
        :param cfg:
        """
        self.filename = filename
        self.file = pathlib.Path(filename)
        self.enabled = cfg.getboolean('enabled', True)
        self.search = cfg['search']
        self.replace = cfg['replace']
        self.date_format = cfg.get('date_format', None)
        self.match = cfg.get('match', 'line')
        self.search_flags = 0
        self.encoding = cfg.get('encoding', 'utf-8')

        search_flags = cfg.get('search_flags', '')
        if search_flags:
            search_flags = re.split(r'\s*,\s*', search_flags)
            for search_flag in search_flags:
                self.search_flags |= getattr(re, search_flag.upper())

    def validate(self):
        """Validate current file configuration

        :raise ValueError:
        """
        if not self.file.exists():
            raise ValueError("File \"%s\" doesn't exists")

        if not self.search:
            raise ValueError("Search cannot be empty")

        if not self.replace:
            raise ValueError("Replace cannot be empty")

        if self.match not in ('file', 'line'):
            raise ValueError("Match must be one of: file, line")

        try:
            codecs.lookup(self.encoding)
        except LookupError:
            raise ValueError("Unknown encoding: \"%s\"" % self.encoding)

    def __repr__(self):
        return '<FileConfig(%s)>' % self.filename


class Config:
    """Configuration"""

    __slots__ = (
        'command',
        'commit',
        'date_format',
        'default_init_version',
        'default_increase_value',
        'files',
        'value',
        'up_part',
        'vcs_commit_message',
        'vcs_engine',
        'vcs_tag_params',
        'verbose',
        'version_file',
    )

    def __init__(self, files=None):
        """Evaluate configuration

        :return:
        """
        self.command = None
        self.commit = False
        self.date_format = defaults.DEFAULT_DATE_FORMAT
        self.default_init_version = defaults.DEFAULT_INIT_VERSION
        self.default_increase_value = defaults.DEFAULT_INCREASE_VALUE
        self.files = []
        self.value = None
        self.up_part = defaults.DEFAULT_UP_PART
        self.vcs_commit_message = defaults.DEFAULT_VCS_COMMIT_MESSAGE
        self.vcs_engine = 'git'
        self.vcs_tag_params = []
        self.verbose = False
        self.version_file = defaults.DEFAULT_VERSION_FILE

        if files:
            self._parse_config_file(files)

    def _parse_config_file(self, cfg_files):
        """Parse config file (ini) and set properties

        :return:
        """
        cfg_handler = configparser.ConfigParser(interpolation=None)

        if not cfg_handler.read(map(str, cfg_files)):
            return

        self._parse_global_section(cfg_handler)
        self._parse_vcs_section(cfg_handler)
        self._parse_file_section(cfg_handler)

    def _parse_global_section(self, cfg_handler):
        """Parse global ([versionner]) section

        :param cfg_handler:
        :return:
        """
        # global configuration
        if 'versionner' in cfg_handler:
            cfg = cfg_handler['versionner']
            if 'file' in cfg:
                self.version_file = cfg['file']
            if 'date_format' in cfg:
                self.date_format = cfg['date_format']
            if 'up_part' in cfg:
                self.up_part = cfg['up_part']
            if 'default_init_version' in cfg:
                self.default_init_version = cfg['default_init_version']
            if 'default_increase_value' in cfg:
                self.default_increase_value = cfg.getint('default_increase_value')

    def _parse_vcs_section(self, cfg_handler):
        """Parse [vcs] section

        :param cfg_handler:
        :return:
        """
        if 'vcs' in cfg_handler:
            cfg = cfg_handler['vcs']
            if 'engine' in cfg:
                self.vcs_engine = cfg['engine']
            if 'tag_params' in cfg:
                self.vcs_tag_params = list(filter(None, cfg['tag_params'].split("\n")))
            if 'commit_message' in cfg:
                self.vcs_commit_message = cfg['commit_message']

    def _parse_file_section(self, cfg_handler):
        """Parse [file:*] sections

        :param cfg_handler:
        :return:
        """

        _number_rxp = re.compile(r'^\d+:(.)')
        # project files configuration
        for section in cfg_handler.sections():
            if section.startswith('file:'):
                path = section[5:]
                path = _number_rxp.sub(r'\1', path)

                project_file = FileConfig(path, cfg_handler[section])

                if not project_file.date_format:
                    project_file.date_format = self.date_format

                if project_file.enabled:
                    try:
                        project_file.validate()
                    except ValueError as exc:
                        print("Incorrect configuration for file \"%s\": %s" % (project_file.filename, exc.args[0]), file=sys.stderr)
                    else:
                        self.files.append(project_file)

    def __repr__(self):
        ret = '<' + self.__class__.__name__ + ': '
        ret += ', '.join('%s=%r' % (name, getattr(self, name)) for name in self.__slots__)
        return ret

"""Commands for versionner
Module defines helpers for searching for commands and aliases for them.
"""

from .command import Command, CommandOutput
from .up import Up
from .tag import Tag
from .set import Set
from .init import Init
from .read import Read


COMMANDS = {
    'up': (Up, 'u'),
    'init': (Init, 'i'),
    'set': (Set, 's'),
    'tag': (Tag, 't'),
    'read': (Read, 'r'),
}
COMMAND_MAPPER = {}
COMMAND_ALIASES = {}


def _manage_commands():
    """Build COMMAND_MAPPER and COMMAND_ALIASES dictionaries using COMMANDS

    @return:None
    """
    for name, (command, *aliases) in COMMANDS.items():
        COMMAND_MAPPER[name] = command
        for alias in aliases:
            COMMAND_MAPPER[alias] = command
        COMMAND_ALIASES[name] = aliases
_manage_commands()
del _manage_commands


def get(name, *args, **kwargs):
    """Find command class for given command name and return it's instance

    :param name: str
    :param args: additional arguments for Command
    :param kwargs: additional arguments for Command
    :return: Command
    """
    cmd = COMMAND_MAPPER.get(name)
    return cmd(*args, **kwargs)


def get_aliases_for(name):
    """Find aliases for given command name

    :param name: str
    :return: Str[]
    """
    return COMMAND_ALIASES[name]

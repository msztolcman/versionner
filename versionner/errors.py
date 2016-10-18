"""
Exceptions for versionner
"""


class VersionnerError(Exception):
    """ Generic versionne error
    """
    ret_code = 2


class ConfigError(VersionnerError):
    """ Configuration error
    """


class InvalidVersionError(VersionnerError):
    """ Bad version string/value error
    """

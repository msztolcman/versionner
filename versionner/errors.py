class VersionnerError(Exception):
    ret_code = 2


class ConfigError(VersionnerError):
    pass


class InvalidVersionError(VersionnerError):
    pass

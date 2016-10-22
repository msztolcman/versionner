"""VCS exceptions"""

class VCSError(RuntimeError):
    """General VCS error"""


class UnknownVCSError(VCSError):
    """Unknwon VCS"""


class VCSStateError(VCSError):
    """VCS state doesn't allow for specified command"""

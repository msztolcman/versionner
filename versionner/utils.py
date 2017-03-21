"""Additional utilities"""

import platform
import sys

from distutils.version import LooseVersion


def validate_python_version():
    """Validate python interpreter version. Only 3.3+ allowed."""
    python_version = LooseVersion(platform.python_version())
    minimal_version = LooseVersion('3.3.0')
    if python_version < minimal_version:
        print("Sorry, Python 3.3+ is required")
        sys.exit(1)

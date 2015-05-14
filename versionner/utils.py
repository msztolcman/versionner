"""
    Additional utilities
"""

import pkg_resources
import platform
import sys


def validate_python_version():
    """
    Validate python interpreter version. Only 3.3+ allowed.
    """
    if pkg_resources.parse_version(platform.python_version()) < pkg_resources.parse_version('3.3.0'):
        print("Sorry, Python 3.3+ is required")
        sys.exit(1)

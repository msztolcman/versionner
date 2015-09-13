from collections import namedtuple
from io import StringIO
import sys

class catch_streams:
    result = namedtuple('Streams', ['out', 'err'])
    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        sys.stdout = StringIO()
        sys.stderr = StringIO()

        return self.result(sys.stdout, sys.stderr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

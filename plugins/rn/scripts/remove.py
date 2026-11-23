"""remove.py, as a maker runs it to remove what it made for itself, in place of `rm`:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/remove.py <path> [<path> ...]`. It runs the code of
remove.py in `domain/remove/`, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported, ahead of this
# file's own folder, so that `remove` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import end
from remove.command import main

if __name__ == "__main__":
    end(lambda: main(sys.argv[1:], os.getcwd()))

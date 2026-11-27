"""role, as Claude Code runs it by rn's hook once one of rn's roles ends:
`python3 ${CLAUDE_PLUGIN_ROOT}/domain/scripts/role ended`, with the hook's input on stdin. It runs
the code of this folder, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# Python puts this folder first on the import path. The code imports its packages from scripts/,
# this folder's parent, so that folder takes its place.
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = SCRIPTS

from fault import end
from host import run

from role.command import main

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(SCRIPTS))
    # stdin is read only for `ended`, so that other arguments print the usage at once.
    given = sys.stdin.read() if sys.argv[1:] == ["ended"] else ""
    end(lambda: main(sys.argv[1:], given, root, run))

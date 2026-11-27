"""steering, as the orchestrator runs it to write where the work stands and to read what's due:
`python3 ${CLAUDE_PLUGIN_ROOT}/domain/scripts/steering <subcommand> <work> ...`. It runs the code of
this folder, whose `command` module says what each subcommand takes and gives."""

from __future__ import annotations

import os
import sys

# Python puts this folder first on the import path. The code imports its packages from scripts/,
# this folder's parent, so that folder takes its place.
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = SCRIPTS

from fault import end

from steering.command import main

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(SCRIPTS))
    end(lambda: main(sys.argv[1:], os.getcwd(), root, sys.stdin.read))

"""tree.py, as the orchestrator runs it to change the run's design tree, and the pruner to check it:
`python3 ${CLAUDE_PLUGIN_ROOT}/domain/scripts/tree.py <subcommand> <run> ...`. It runs the code of
tree.py in `domain/tree/`, whose `command` module says what each subcommand takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, this folder's parent, which comes on the import path before it's
# imported, ahead of this file's own folder, so that `tree` names the package there and not this
# file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fault import end
from repository.host import run
from tree.command import main

if __name__ == "__main__":
    end(
        lambda: main(
            sys.argv[1:], os.getcwd(), os.path.dirname(os.path.dirname(HERE)), run, sys.stdin.read
        )
    )

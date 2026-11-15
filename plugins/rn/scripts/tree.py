"""tree.py, as the orchestrator and each role run it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py
<command> ...`. It runs the code of tree.py in `domain/tree/`, whose `command` module says what each
command takes and gives."""

from __future__ import annotations

import os
import sys

# domain/ comes first on the import path, so that `tree` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import end
from tree.command import main

if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin, os.getcwd(), os.path.dirname(HERE)))

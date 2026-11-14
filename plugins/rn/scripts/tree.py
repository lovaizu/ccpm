"""tree.py, as rn's orchestrator and roles run it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py
<command>`. It runs the code of tree.py in `domain/tree/`, whose `command` module says each command
and what it gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "domain"))

from fault import end
from tree.command import main

if __name__ == "__main__":
    end(main(sys.argv[1:], os.environ, os.getcwd()))

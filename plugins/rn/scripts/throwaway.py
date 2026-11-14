"""throwaway.py, as rn's generator runs it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py try
<run> <deliverable> <round> <command>`. It runs the code of throwaway.py in `domain/`."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "domain"))

from fault import end
from throwaway import main as run_command

if __name__ == "__main__":
    end(run_command(sys.argv[1:], os.environ, os.getcwd()))

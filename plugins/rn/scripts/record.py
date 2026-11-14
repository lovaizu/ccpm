"""record.py, as rn's orchestrator and roles run it to record each step and practice, and as the
guard runs it at each end: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py <command>`. It runs the
code of record.py in `domain/record/`, whose `command` module says each command and what it
gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from record.command import main

if __name__ == "__main__":
    exit_code, printed, said = main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE))
    print(printed, end="")
    print(said, end="", file=sys.stderr)
    sys.exit(exit_code)

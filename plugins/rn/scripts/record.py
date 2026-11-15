"""record.py, as each role and the orchestrator record their work, and as the guard runs rn's check
at each end: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py <command> ...`. It runs the code in
`domain/record/`, whose `command` module says what each command takes and gives."""

from __future__ import annotations

import os
import sys

# The package of the same name in domain/ is the one imported, so domain/ leads the import path.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import end
from record.command import main

if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE)))

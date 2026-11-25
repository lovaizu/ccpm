"""check, as a role runs it before it ends, to hold its result to its Cut: `python3
${CLAUDE_PLUGIN_ROOT}/domain/scripts/check <role> <cut>`. It runs the code of this folder, whose
`command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# Python puts this folder first on the import path. The code imports its packages from scripts/,
# this folder's parent, so that folder takes its place.
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = SCRIPTS

from fault import end

from check.command import main

if __name__ == "__main__":
    end(lambda: main(sys.argv[1:], os.getcwd(), os.path.dirname(os.path.dirname(SCRIPTS))))

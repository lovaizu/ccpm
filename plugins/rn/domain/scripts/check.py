"""check.py, as a role runs it before it ends, to hold its result to its Cut: `python3
${CLAUDE_PLUGIN_ROOT}/domain/scripts/check.py <role> <cut>`. It runs the code of check.py in
`domain/check/`, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, this folder's parent, which comes on the import path before it's
# imported, ahead of this file's own folder, so that `check` names the package there and not this
# file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from check.command import main
from fault import end

if __name__ == "__main__":
    end(lambda: main(sys.argv[1:], os.getcwd(), os.path.dirname(os.path.dirname(HERE))))

"""check.py, as Lane's check at a role's end runs it to hold the role's result to its Cut:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <role> <cut>`. It runs the code of check.py in
`domain/check/`, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported, ahead of this
# file's own folder, so that `check` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from check.command import main
from fault import end

if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE)))

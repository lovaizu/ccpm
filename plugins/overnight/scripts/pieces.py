"""pieces.py, as status runs it to show where each piece stands:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py report`. It runs the code of pieces in
`domain/pieces/`, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported, ahead of this
# file's own folder, so that `pieces` names the package there and not this file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "domain"))

from pieces.command import main

if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)

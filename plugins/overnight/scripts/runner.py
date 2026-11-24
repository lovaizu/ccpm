"""runner.py, as hand-over starts it apart from the session to carry one piece, by the command
line that `runner.command.line` gives. It runs the code of runner in `domain/runner/`, whose
`command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported, ahead of this
# file's own folder, so that `runner` names the package there and not this file.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "domain"))

from runner.command import main

if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], sys.stdin.read())
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)

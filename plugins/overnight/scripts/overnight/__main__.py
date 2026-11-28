"""overnight, as bin/overnight runs it: `python3 <plugin>/scripts/overnight ...`. It runs the code
of this folder, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# Python puts this folder first on the import path. The code imports its package from scripts/,
# this folder's parent, so that folder takes its place. Also in ../carry/__main__.py.
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = SCRIPTS

from overnight.command import main

if __name__ == "__main__":
    main(sys.argv[1:], os.path.dirname(SCRIPTS))

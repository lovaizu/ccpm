"""template.py, as ccpm's developers and rn run it to hold a document to its kind's template:
`python3 ${CLAUDE_PLUGIN_ROOT}/domain/scripts/template.py <kind> <document> [<language>]`. It runs
the code of template.py in `domain/template/`, whose `command` module says what it takes and
gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, this folder's parent, which comes on the import path before it's
# imported, ahead of this file's own folder, so that `template` names the package there and not
# this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fault import end
from template.command import main

if __name__ == "__main__":
    end(lambda: main(sys.argv[1:], os.getcwd(), os.path.dirname(os.path.dirname(HERE))))

"""repository.py, as the orchestrator and each role run it to act on the user's repository: `python3
${CLAUDE_PLUGIN_ROOT}/domain/scripts/repository.py <subcommand> ...`. It runs the code of
repository.py in `domain/repository/`, whose `command` module says what each subcommand takes and
gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, this folder's parent, which comes on the import path before it's
# imported, ahead of this file's own folder, so that `repository` names the package there and not
# this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fault import end
from repository.command import main
from repository.host import run

if __name__ == "__main__":
    end(lambda: main(sys.argv[1:], os.getcwd(), os.path.dirname(os.path.dirname(HERE)), run))

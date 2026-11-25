"""hook, as Claude Code runs it before each Bash command and each Write or Edit, by rn's
`hooks/hooks.json`: `python3 "${CLAUDE_PLUGIN_ROOT}/domain/scripts/hook"`, with the hook's input on
stdin. It runs the code of this folder, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# Python puts this folder first on the import path. The code imports its packages from scripts/,
# this folder's parent, so that folder takes its place.
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[0] = SCRIPTS

from fault import end

from hook.command import main

if __name__ == "__main__":
    end(lambda: main(sys.stdin.buffer.read(), os.path.dirname(os.path.dirname(SCRIPTS))))

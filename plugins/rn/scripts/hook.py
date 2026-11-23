"""hook.py, as Claude Code runs it before each Bash command, by rn's `hooks/hooks.json`:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"`, with the hook's input on stdin. It runs the
code of hook.py in `domain/hook/`, whose `command` module says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path before it's imported, ahead of this
# file's own folder, so that `hook` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import end
from hook.command import main

if __name__ == "__main__":
    end(lambda: main(sys.stdin.buffer.read(), os.path.dirname(HERE)))

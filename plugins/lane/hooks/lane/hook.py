"""hook.py, which Claude Code runs on each hook event of the plugin as hooks.json says: how that run
reaches the guard's code in domain/, which events.py and guard.py hold."""

from __future__ import annotations

import os
import sys

# The guard's code lies in domain/, which comes first on the import path, so that this file needs
# nothing but Python's standard library and the plugin's folder.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "domain"))

from events import Output, read_event, write_answer
from guard import handle


def main(stdin: str, root: str) -> Output:
    """The hook's output for the event on standard input, in the plugin whose folder is root."""
    event = read_event(stdin)
    return write_answer(event, handle(event, root))


if __name__ == "__main__":
    out = main(sys.stdin.read(), os.path.dirname(os.path.dirname(HERE)))
    sys.stdout.write(out.stdout)
    sys.stderr.write(out.stderr)
    raise SystemExit(out.code)

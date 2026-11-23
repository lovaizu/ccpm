"""queue.py, as each skill of overnight and the stacker run it:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/queue.py stack <queue file>`,
`queue.py check [<queue file>]`, and `queue.py run`, which the stacker starts apart from Claude
Code with the stacked queue on its standard input. Each subcommand runs the `command` module of its
part in `domain/`, which says what it takes and gives."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which takes the place of this file's own folder on the import path, so
# that the standard library's `queue`, which threads import, isn't this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[0] = os.path.join(HERE, "..", "domain")

from checker import command as checker
from runner import command as runner
from stacker import command as stacker

USAGE = """\
usage: queue.py stack <queue file>
       queue.py check [<queue file>]
       queue.py run
"""


def main(argv: list[str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `queue.py` with the arguments: what the part of the
    subcommand gives, or 2 with the usage where the subcommand is none of stack, check, and run."""
    plugin_root = os.path.dirname(HERE)
    if argv[:1] == ["stack"]:
        return stacker.main(argv[1:], os.getcwd())
    if argv[:1] == ["check"]:
        return checker.main(argv[1:], os.getcwd(), plugin_root)
    if argv[:1] == ["run"]:
        return runner.main(argv[1:], sys.stdin.read())
    return 2, "", USAGE


if __name__ == "__main__":
    code, printed, said = main(sys.argv[1:])
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(code)

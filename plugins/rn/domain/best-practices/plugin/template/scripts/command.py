"""What a role or the person runs, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<command>.py <args>`:
<what it checks or does>. It gives 0 where it finds no problem, 1 with each problem it finds, and
2 with why where it can't check.

DELETE_TEMPLATE_COMMENT: <command>, <args>, <what it checks or does>: the command as its steps name
it, and what it gives, so that a role reads the result by its exit code. It needs only Python 3.9
and the standard library, as python3 is wherever git is."""

from __future__ import annotations

import sys

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<command>.py <args>"


def main(argv: list[str]) -> int:
    """Runs the command on its arguments, and gives the exit code that the module names."""
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


# Run as the command, and not when a test imports it.
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

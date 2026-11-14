"""The result script, which a role runs as `python3 <plugin>/hooks/lane/result.py <role> <result>`
to give its result: it refuses a result that the role may not give, and one that no Run of the
conversation, whose ID Claude Code gives each Bash command as `CLAUDE_CODE_SESSION_ID`, holds. The
guard adds the Result to the run record at the PostToolUse of a run that gave 0, as only that
payload names the subagent that ran it."""

from __future__ import annotations

import sys
from collections.abc import Mapping


def main(argv: list[str], environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `result.py <role> <result>`: 0 and the result given,
    where the laid set of the plugin that holds this script lets the role give it, and a Run of the
    conversation that goes on holds the role, as the skill of the Run or the role of a Start that
    runs, each Run as `routes.stand`, the guard's code, works it out from the run record; 1 with the
    results that the role may give where it may give no such result, or with why where no such Run
    holds the role; 2 with the usage where the arguments aren't a role and a result. It writes
    nothing to the run record."""
    raise NotImplementedError("result.main")


if __name__ == "__main__":
    import os

    code, out, err = main(sys.argv[1:], os.environ)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)

"""The result script, which a role runs as `python3 <plugin>/hooks/lane/result.py <role> <result>`
to give its result: it records the Result in the conversation's Run, whose ID Claude Code gives
each Bash command as `CLAUDE_CODE_SESSION_ID`, and refuses a result that the role may not give."""

from __future__ import annotations

import sys
from collections.abc import Mapping


def main(argv: list[str], environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `result.py <role> <result>`: 0 and the Result recorded,
    in the laid set of the plugin that holds this script and the Run of the conversation; 1 with
    the results that the role may give where it may give no such result, or with why where no Run
    of the conversation holds the role's call of result.py; 2 with the usage where the arguments
    aren't a role and a result."""
    raise NotImplementedError("result.main")


if __name__ == "__main__":
    import os

    code, out, err = main(sys.argv[1:], os.environ)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)

"""The result script, by which a role or the skill gives its result, as
`python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <role> <result>`. It decides nothing of its own:
it refuses a result that routes.py says the role may not give, in case the guard didn't check the
command. The guard keeps the result from the hook event of the command.

Exit codes: 0 for a result that the role may give, 1 for one it may not or where the lanes laid
can't tell, and 2 for a command in another form.
"""

from __future__ import annotations

import os
import sys
from typing import IO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "domain"))

import laid
import lanes
import routes


def main(argv: list[str], err: IO[str], root: str) -> int:
    """Gives the exit code for the result in argv, of the plugin at the root, and writes why to err
    where it refuses the result."""
    if len(argv) != 3:
        err.write("result.py: run it as `result.py <role> <result>`\n")
        return 2
    name, given = argv[1], argv[2]
    try:
        found = laid.read(root)
    except laid.Unlaid as why:
        err.write(f"result.py: can't tell which results {name} may give: {why}\n")
        return 1
    allowed = routes.allowed(found, name)
    if given in allowed:
        return 0
    err.write(
        f"result.py: {name} may give {lanes.listed(allowed)}, and `{given}` is none of them\n"
    )
    return 1


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
    sys.exit(main(sys.argv, sys.stderr, here))

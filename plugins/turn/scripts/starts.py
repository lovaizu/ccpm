"""What the role before a step runs, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/starts.py <run>
<role>`: the run values of each run of the role's step, a line of JSON each, which the role puts in
its reply for up to start each run with, giving 0; or why it cannot, giving 2. It hands the reading
to runs.py in core/domain/."""

from __future__ import annotations

import json
import os
import sys

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
from runs import ROLES, runs

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/starts.py <run>"
    " builder|evaluator|refactorer|proofreader"
)


def main(argv: list[str]) -> int:
    """Prints the runs of the role's step in the run's folder given, and gives 0, or 2 where it
    cannot read them; or prints the usage and gives 2."""
    if len(argv) != 2 or argv[1] not in ROLES:
        print(USAGE, file=sys.stderr)
        return 2
    run, role = argv
    try:
        found = runs(run, role)
    except files.Unreadable as why:
        print(f"starts.py: could not give the runs of {role}: {why}", file=sys.stderr)
        return 2
    print(f"Runs of turn:{role}, each started with its line:")
    for values in found:
        print(json.dumps(values, ensure_ascii=False))
    return 0


# Run as the command, and not when the tests import it under the name starts.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

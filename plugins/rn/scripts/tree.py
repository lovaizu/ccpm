"""What the main conversation and rn's roles run on the work's design tree, from the top of the
repository, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py <command> <args>`:

- `change`: the change on its standard input kept for the planner's next start;
- `start <role>`: the cut for the start of the planner, the generator, or the evaluator;
- `points`, `status`: the points open of the run at hand, and where it stands;
- `write <run> <edit>`, `commit <run>`, `deliver <run>`, `report <run>`: the planner's tree edit
  written, the change committed, a deliverable done committed and pushed, and the report;
- `record <path>`: a Making record or an Answers checked;
- `check <tree>`: a design tree's form, order, and statuses against preconditions checked.

Each prints what its reader acts on and gives 0; or prints what's wrong and gives 1; or prints why
it can't read what it needs and gives 2. It needs only Python 3.9 and its standard library, and
git, and gh for the pull request."""

from __future__ import annotations

import os
import sys
from typing import Callable

# rn's code, in domain/ beside this folder, first on the path, as no module before it has a name
# of rn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domain"),
)

import edits
import files
import records
import repository
import starts

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py change < <change>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py start planner|generator|evaluator\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py points|status\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py write <run> <edit>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py commit|deliver|report <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py record <path>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py check <tree>"
)
# Each command, by its name and the number of its arguments, and what it does with them.
COMMANDS: dict[tuple[str, int], Callable[..., str]] = {
    ("change", 0): lambda: starts.change(sys.stdin.read()),
    ("start", 1): starts.start,
    ("points", 0): starts.points,
    ("status", 0): starts.status,
    ("write", 2): edits.write,
    ("commit", 1): edits.commit,
    ("deliver", 1): edits.deliver,
    ("report", 1): edits.report,
    ("record", 1): records.record,
}


def check(path: str) -> int:
    """Checks the design tree at the path, and gives 0, 1 or 2 as the module says."""
    try:
        found = edits.check(path)
    except files.Unreadable as why:
        print(f"tree.py: {path} can't be checked: {why}", file=sys.stderr)
        return 2
    for fault in found:
        print(f"tree.py: {path}: {fault}", file=sys.stderr)
    if not found:
        print(f"tree.py: {path} holds.")
    return 1 if found else 0


def main(argv: list[str]) -> int:
    """Runs the command on its arguments, and gives 0, 1 or 2 as the module says."""
    if argv[:1] == ["check"] and len(argv) == 2:
        return check(argv[1])
    found = COMMANDS.get((argv[0], len(argv) - 1)) if argv else None
    if found is None:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        said = found(*argv[1:])
    except starts.Stop as why:
        print(f"tree.py: {why}", file=sys.stderr)
        return 1
    except (files.Unreadable, repository.Failed) as why:
        print(f"tree.py: can't {argv[0]}: {why}", file=sys.stderr)
        return 2
    print(said)
    return 0


# Run as the command, and not when a test imports it.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

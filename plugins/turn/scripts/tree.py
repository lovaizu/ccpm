"""What designer runs on a run's folder, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py check
<run>` and `... parts <run>`: check, whether the design tree asks each question of the template
and the work's parts and remake hold, giving 0, 1 with each fault, or 2 with why it could not
check; and parts, the decisions split into the parts written into work.json, giving 0, or 2. It
hands each to designs.py in core/domain/."""

from __future__ import annotations

import os
import sys

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
from designs import check, parted

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py check|parts <run>"
HOLDS = (
    "the tree asks each question of the template as it asks it, and the work's parts and the"
    " remake hold."
)


def checked(run: str) -> int:
    """Prints whether the run's design holds, and gives 0, 1 or 2."""
    try:
        found = check(run)
    except files.Unreadable as why:
        print(f"tree.py: could not check {run}: {why}", file=sys.stderr)
        return 2
    if found:
        print(f"tree.py: {run} does not hold:")
        for fault in found:
            print(f"- {fault}")
        return 1
    print(f"tree.py: {run} holds: {HOLDS}")
    return 0


def split(run: str) -> int:
    """Writes the parts of the run's tree into its work.json, made where it is not there, says
    them, and gives 0, or 2 where a file cannot be read."""
    path = os.path.join(run, "work.json")
    try:
        tree = files.load(os.path.join(run, "design-tree.json"), "design-tree")
        work = (
            files.load(path, "work")
            if os.path.exists(path)
            else {"paths": [], "commands": [], "parts": []}
        )
    except files.Unreadable as why:
        print(f"tree.py: could not split {run}: {why}", file=sys.stderr)
        return 2
    made = parted(work, tree)
    files.save(path, made)
    said = "; ".join(f"{p['id']} {', '.join(p['decisions'])}" for p in made["parts"])
    print(
        f"tree.py: wrote the parts into {path}: {said}. Give each part its paths, and join two"
        " parts whose files meet."
    )
    return 0


def main(argv: list[str]) -> int:
    """Runs the command on the run's folder given, or prints the usage and gives 2."""
    if len(argv) != 2 or argv[0] not in ("check", "parts"):
        print(USAGE, file=sys.stderr)
        return 2
    return checked(argv[1]) if argv[0] == "check" else split(argv[1])


# Run as the command, and not when the tests import it under the name tree.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

"""What the generator runs once it has made the deliverable, as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>` from the top of the repository: the commands of
the round's Making record run in a throwaway copy with a throwaway home, and what each gave
written into the round's try record, `throwaway.txt`, which the evaluators read. It gives 0 with
the try record's path; 1 with what's wrong, such as a file named out of the home, running
nothing; and 2 with why where it can't read the run."""

from __future__ import annotations

import os
import sys

# rn's code, in domain/ beside this folder, first on the path, as no module before it has a name
# of rn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domain"),
)

import files
import starts
import tries

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>"


def main(argv: list[str]) -> int:
    """Tries the round's commands of the run given, and gives 0, 1 or 2 as the module says."""
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        (run,) = argv
        path = tries.tried(run)
    except starts.Stop as why:
        print(f"throwaway.py: {why}", file=sys.stderr)
        return 1
    except files.Unreadable as why:
        print(f"throwaway.py: can't try the commands: {why}", file=sys.stderr)
        return 2
    print(f"throwaway.py: the try record is {path}. Read it whole before you judge.")
    return 0


# Run as the command, and not when a test imports it.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

"""What builder, evaluator, refactorer and proofreader run on their answers file, as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/answers.py check <run> <answers>`: 0 where every question their run
was given is answered once and each line lies in the work, 1 with each fault, and 2 with why it
could not check. It hands the check to answering.py in core/domain/."""

from __future__ import annotations

import os
import sys

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
from answering import assigned, check

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/answers.py check <run> <answers>"


def main(argv: list[str]) -> int:
    """Checks the answers at the path given in the run's folder given, prints what it found, and
    gives 0, 1 or 2; or prints the usage and gives 2."""
    if len(argv) != 3 or argv[0] != "check":
        print(USAGE, file=sys.stderr)
        return 2
    run, path = argv[1], argv[2]
    try:
        found = check(run, path)
    except files.Unreadable as why:
        print(f"answers.py: could not check {path}: {why}", file=sys.stderr)
        return 2
    if found:
        print(f"answers.py: {path} does not hold:")
        for fault in found:
            print(f"- {fault}")
        return 1
    given = assigned(run, os.path.relpath(path, run).replace(os.sep, "/"))
    print(f"answers.py: {path} answers each question it was given: {', '.join(given)}.")
    return 0


# Run as the command, and not when the tests import it under the name answers.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

"""Checks each of rn's best practices against its schema,
`dev/rn/best-practice.schema.json`. Run it from the top of the repository as
`python3 dev/scripts/practices.py <best practice json>...`. It gives 0, or 1 where it names a fault,
and 2 with its usage where it gets no file. It's ccpm's own tooling, kept out of rn's folder, as no
run of rn checks the form of rn's own best practices."""

from __future__ import annotations

import os
import sys

# The top of the repository.
TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# rn's form check, which reads a value against one of rn's schemas.
RN = os.path.join(TOP, "plugins", "rn", "domain")
sys.path.insert(0, os.path.join(RN, "scripts"))

from fault import Wrong
from form import held

SCHEMA = os.path.join(TOP, "dev", "rn", "best-practice.schema.json")
USAGE = "usage: python3 dev/scripts/practices.py <best practice json>..."


def main(paths: list[str]) -> int:
    """Checks each file given, as the module says."""
    if not paths:
        print(USAGE, file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        try:
            held(path, SCHEMA, "the best practice")
        except Wrong as why:
            print(f"practices.py: {why}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

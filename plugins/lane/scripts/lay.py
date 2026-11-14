"""Lane's script that up runs: `lay.py types` gives each lane type for up to propose from,
`lay.py print <plugin> <proposal.json>` checks the Proposal that up wrote and shows it, and
`lay.py write <plugin> <ID>` lays the Proposal of the ID, which its caller approved, into the
plugin. It imports the lane types from `hooks/lane/`, the code it copies into each plugin."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks", "lane"))

USAGE = "usage: lay.py types | print <plugin> <proposal.json> | write <plugin> <ID>"


def types_text() -> str:
    """What `lay.py types` prints: for each lane type, its name, what it takes, the steps it suits,
    and its sentence as it reads on an example."""
    raise NotImplementedError("lay.types_text")


def main(argv: list[str], environ: Mapping[str, str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `lay.py` with the arguments, from the folder `cwd`,
    where `<plugin>` is the plugin's folder from there: 0 with what `types`, `print`, or `write`
    prints; 1 with what's wrong where the Proposal can't stand, where no Proposal has the ID or
    the Steps changed since it was shown, or where `claude plugin validate` fails after laying,
    with what it said; 2 with the usage where the arguments are none of these."""
    raise NotImplementedError("lay.main")


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], os.environ, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)

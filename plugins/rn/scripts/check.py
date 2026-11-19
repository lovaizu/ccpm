"""check.py, as Lane runs it at a role's end, for the step that ends on rn's own check:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <role> {cut}`, with the role generator or evaluator
and the Cut its start was given. It gives 0 where the result holds, and 1 with each fault for the
role to mend before it ends."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path ahead of this file's own folder, so
# that `check` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from check import evaluator, generator
from fault import end

USAGE = "usage: check.py generator|evaluator <cut>\n"


def main(argv: list[str], cwd: str, plugin: str) -> tuple[int, str, str]:
    """Runs `<role> <cut>` through generator.faults or evaluator.faults.

    Takes: the arguments, the worktree it runs in, and rn's folder.
    Gives: 0 where the result holds; 1 with each fault, a line each; 2 with the usage where the
    arguments aren't a role and a Cut. Where the Cut that Lane gives isn't there or in its form,
    Wrong stops it with its trace, as rn's adapter wrote that Cut."""
    if len(argv) != 2 or argv[0] not in ("generator", "evaluator"):
        return 2, "", USAGE
    role, cut = argv
    run = os.path.join(cwd, os.path.dirname(os.path.dirname(os.path.dirname(cut))))
    if role == "generator":
        found = generator.faults(run, cut, plugin, cwd)
    else:
        found = evaluator.faults(run, cut, plugin)
    return (1, "", "".join(f"{each}\n" for each in found)) if found else (0, "", "")


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE)))

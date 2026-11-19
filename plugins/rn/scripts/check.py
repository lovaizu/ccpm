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

from fault import end


def main(argv: list[str], cwd: str, plugin: str) -> tuple[int, str, str]:
    """Runs `<role> <cut>` through generator.faults or evaluator.faults.

    Takes: the arguments, the worktree it runs in, and rn's folder.
    Gives: 0 where the result holds; 1 with each fault, a line each, or with what Wrong says; 2
    with the usage where the arguments aren't a role and a Cut."""
    raise NotImplementedError("check.main")


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE)))

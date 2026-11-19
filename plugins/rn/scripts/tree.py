"""tree.py, as rn's orchestrator runs it to commit a change of the run's folder:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py commit <run> '<ground>'`, in the run's worktree. It
gives 0 with the commit's hash once the design tree holds its form, and 1 with the first fault
otherwise, leaving git as it was."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path ahead of this file's own folder, so
# that `tree` names the package there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import end


def main(argv: list[str], cwd: str, plugin: str) -> tuple[int, str, str]:
    """Runs `commit <run> <ground>` through commit.commit.

    Takes: the arguments, the worktree it runs in, and rn's folder.
    Gives: 0 with the hash; 1 with what Wrong or Missing says; 2 with the usage where the arguments
    aren't `commit`, a run, and a ground, or with what CantRun says."""
    raise NotImplementedError("tree.main")


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd(), os.path.dirname(HERE)))

"""Decides check.py's command line: what it takes, what it prints, and the exit code by which Lane
reads its result."""

from __future__ import annotations

from collections.abc import Sequence

USAGE = """\
usage: check.py <role> <cut>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `check.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`.

    `<role> <cut>`, the role's Cut by its path from `cwd`: 0 printing nothing where the Cut holds
    its schema and `check.result.faults` finds no fault in the role's result beside it, with the
    run's worktree that the Cut's paths give and `cwd`; 1 with each
    fault a line, or, where the role wrote no result, the path where it writes one. 1 with
    `check.py: <what's wrong>` where the input is Wrong, saying how to mend it; 2 with what stopped
    it where it CantRun; 2 with the usage where the arguments are other than a role and a Cut.
    """
    raise NotImplementedError("check.command.main")

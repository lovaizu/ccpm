#!/usr/bin/env python3
"""rn's adapter of the Kept results, which Lane's guard runs as `hooks/adapters/kept_results.py`
with no argument, in the folder that the conversation works in, to pick a run up in a new
conversation, as the user types /rn:up at the root of the repository. It decides which run's
results the conversation picks up, and how the results that rn's check kept in each role's record
read in Lane's form, `{"results": [{"role", "result"}, ...]}`, in the order of the roles' starts
that tree.py's cut gives."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))


def kept(cwd: str) -> list[tuple[str, str]]:
    """Each role and the result that rn's check kept in its record, in the order of the roles'
    starts, of the run of the worktree that holds `cwd`, or else of the one run left in the
    repository that holds `cwd`; none where no run is left, or more than one, as the adapter can't
    tell which one the user picks, and the guard then starts the run anew."""
    raise NotImplementedError("kept_results.kept")


def main(argv: list[str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter: 0 with `{"results": [...]}`; 1 with why,
    naming the record, where a record isn't in its form; 2 with the usage where it's given an
    argument."""
    raise NotImplementedError("kept_results.main")


if __name__ == "__main__":
    exit_code, printed, said = main(sys.argv[1:], os.getcwd())
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(exit_code)

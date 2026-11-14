#!/usr/bin/env python3
"""rn's adapter of the Kept results, which Lane's guard runs as `hooks/adapters/kept_results.py`
with no argument, in the folder that the conversation works in, to pick a run up in a new
conversation. It decides how the results that rn's check kept in each role's record read in Lane's
form, `{"results": [{"role", "result"}, ...]}`, in the order of the roles' starts."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))


def kept(cwd: str) -> list[tuple[str, str]]:
    """Each role and the result that rn's check kept in its record, in the run of the worktree that
    holds `cwd`, in the order of the roles' starts; none where `cwd` lies in no run's worktree, as a
    conversation outside a run picks no run up."""
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

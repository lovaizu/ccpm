#!/usr/bin/env python3
"""rn's adapter of the Kept results, which Lane's guard runs as `hooks/adapters/kept_results.py`
with no argument and `{"args": ...}` on stdin, the words typed after /rn:up, in the folder that the
conversation works in. It decides whether the call starts a new run, as a request does whatever
runs are left, or picks one up, as /rn:up alone does; which run's results /rn:up alone picks up;
and how the results that rn's check kept in each role's record read in Lane's form,
`{"results": [{"role", "result"}, ...]}`, in the order of the roles' starts that tree.py's cut
gives."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))

from fault import end


def kept(args: str, cwd: str) -> list[tuple[str, str]]:
    """Each role and the result that rn's check kept in its record, in the order of the roles'
    starts, for a call of /rn:up with the words `args`: none where `args` holds a request, any
    words but white space, as a request starts a new run whatever runs are left; else, of the run
    of the worktree that holds `cwd`, or else of the one run left in the repository that holds
    `cwd`; none where no run is left, or more than one, as the adapter can't tell which one the
    user picks, and the guard then starts the run anew."""
    raise NotImplementedError("kept_results.kept")


def main(argv: list[str], stdin: str, cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter with the arguments and the standard input:
    0 with `{"results": [...]}`; 1 with why, where stdin isn't `{"args": <words>}`, or naming the
    record, where a record isn't in its form; 2 with the usage where it's given an argument."""
    raise NotImplementedError("kept_results.main")


if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin.read(), os.getcwd()))

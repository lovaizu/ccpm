"""Decides what the work still has to fill in what it makes: each line marked `TODO:` that its
branch adds to the repository beside the default branch, committed or not, outside rn's own
`.rn/`, as the work places each deliverable's parts that a later task makes as TODO."""

from __future__ import annotations

import os
import re

from fault import Missing
from host import Host

# The mark of a part that a later task makes, in its common form, `TODO:`; words that only name the
# mark, without it or quoted as code, pass.
_MARK = re.compile(r"(?<!`)\bTODO:")
# Where a hunk of `git diff --unified=0` starts in the new file: `@@ -a,b +c,d @@`.
_HUNK = re.compile(r"^@@ -\S+ \+(\d+)")
# What the work makes, rn's own records of the work left out.
_MADE = [".", ":(exclude).rn"]


def left(worktree: str, host: Host) -> list[str]:
    """Each TODO that the work adds, by its place.

    Takes: the worktree rn runs in, and the host.
    Gives: each line marked `TODO:`, as `<path>:<line>: <its words>`, by path and line, of what
    the worktree changes and adds beside where its branch left the default branch of `origin`,
    committed or not; none where there's none.
    Changes: nothing.
    Refuses: Missing where `origin` names no default branch, saying how to name it.
    """
    base = _base(worktree, host)
    diff = host(["git", "diff", "--unified=0", "--no-color", base, "--", *_MADE], worktree).out
    found = _added(diff)
    others = host(["git", "ls-files", "--others", "--exclude-standard", "--", *_MADE], worktree)
    for path in others.out.splitlines():
        with open(os.path.join(worktree, path), encoding="utf-8", errors="replace") as f:
            found += [(path, n, line) for n, line in enumerate(f.read().splitlines(), 1)]
    return [f"{path}:{n}: {line}" for path, n, line in sorted(found) if _MARK.search(line)]


def _base(worktree: str, host: Host) -> str:
    named = host(["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], worktree)
    if named.code != 0:
        raise Missing(
            "origin names no default branch, so the work's own TODOs can't be told apart;"
            " name it by `git remote set-head origin --auto`"
        )
    return host(["git", "merge-base", "HEAD", named.out.strip()], worktree).out.strip()


def _added(diff: str) -> list[tuple[str, int, str]]:
    """Each line that the diff adds, with its path and its line in the new file."""
    found = []
    path, line = "", 0
    for each in diff.splitlines():
        hunk = _HUNK.match(each)
        if each.startswith("+++ "):
            path = each[len("+++ b/") :]
        elif hunk:
            line = int(hunk.group(1))
        elif each.startswith("+"):
            found.append((path, line, each[1:]))
            line += 1
    return found

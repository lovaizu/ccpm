"""Decides whether a file is a run's design tree, `.rn/<name>/design-tree.json` under any folder,
as the hook keeps each write to it to the pruner, by a path written with `/` or with `\\`, as
Claude Code gives a path on each OS."""

from __future__ import annotations

import re

# The design tree's file in a run's folder, as the architecture's Directory structure names it.
TREE = "design-tree.json"
# rn's folder on the work's branch, which holds each run's folder.
RN_FOLDER = ".rn"


def is_tree(path: str) -> bool:
    """Whether the path, absolute as Claude Code gives a file tool's `file_path`, is a run's
    design tree: its last three parts `.rn`, one folder, and `design-tree.json`."""
    parts = re.split(r"[\\/]", path)
    return parts[-1] == TREE and parts[-3:-2] == [RN_FOLDER]

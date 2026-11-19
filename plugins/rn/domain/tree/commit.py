"""Decides that a change of the design tree reaches git only once the tree holds its form."""

from __future__ import annotations

import os

from tree import design, git


def commit(top: str, run: str, plugin: str, ground: str) -> str:
    """Commits a change of the run's folder, as S1 and S2 of rn's architecture commit each change.

    Takes: the top of the run's worktree, the run's folder, rn's folder, and the ground of the
    change.
    Gives: the commit's hash, once design.read holds the tree.
    Changes: the work's branch, through git.commit.
    Refuses: each refusal of design.read, before any commit, and each of git.commit."""
    design.read(os.path.join(top, run), plugin)
    return git.commit(top, run, ground)

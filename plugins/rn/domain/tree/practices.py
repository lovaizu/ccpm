"""Decides where the best practice of each kind lies for a run: the one made on a run, in
`.rn/best-practices/<kind>/` of the run's worktree, over rn's own of that kind."""

from __future__ import annotations

from tree.runs import Run


def folder(run: Run, plugin_root: str, kind: str) -> str:
    """The folder of a kind's best practice.

    Takes: the run, rn's folder, and the kind, such as readme.
    Gives: the folder of the run's own best practice of the kind where it has one, or else rn's own.
    Changes: nothing.
    Refuses: fault.Wrong, naming the kinds there are, where neither has the kind.
    Carries: S1 `A->>T: gets ... the Cut`, which names the best practice of the role's kind; and
    record.py's check, which reads that best practice's practices and template.
    """
    raise NotImplementedError("practices.folder")

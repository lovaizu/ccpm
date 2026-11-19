"""Decides when a generator's result holds: its form, each decision of its Cut named where it's
carried out, and its document held to its kind's template, so that a Round rests only on a
deliverable made from its Cut."""

from __future__ import annotations

from collections.abc import Sequence


def faults(run: str, cut: str, plugin: str, top: str) -> Sequence[str]:
    """Each fault of the generator's result beside its Cut.

    Takes: the run's folder, the path of the Cut, rn's folder, and the top of the worktree, where
    the deliverable lies.
    Gives: one line for each fault: the result missing or out of `schemas/generator.schema.json`, a
    decision of the Cut that the result names nowhere, or a fault of template.check where the
    deliverable's kind has a template; none where the result holds.
    Refuses: Wrong, naming the file, where the Cut isn't there or isn't in its form."""
    raise NotImplementedError("generator.faults")

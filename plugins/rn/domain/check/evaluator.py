"""Decides when an evaluator's result holds: its form, and each condition of its group answered
once, good with the lines that meet it or more with what its people get once it's good."""

from __future__ import annotations

from collections.abc import Sequence


def faults(run: str, cut: str, plugin: str) -> Sequence[str]:
    """Each fault of an evaluator's result beside its Cut.

    Takes: the run's folder, the path of the Cut, and rn's folder.
    Gives: one line for each fault: the result missing or out of
    `schemas/evaluator.schema.json`, or a condition of the Cut's group answered twice or not at all;
    none where the result holds.
    Refuses: Wrong, naming the file, where the Cut isn't there or isn't in its form."""
    raise NotImplementedError("evaluator.faults")

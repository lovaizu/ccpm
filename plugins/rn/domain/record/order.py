"""Decides the order that a record must keep: each step of the prompt in its order, and each
practice of each best practice within the step that takes its phase, such as the generator's
deciding and making steps."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from record.form import Record
from record.practices import Practice


def lacks(
    record: Record, of: str, steps: Sequence[int], practices: Mapping[str, Sequence[Practice]]
) -> tuple[str, ...]:
    """What a record lacks of the steps and practices.

    Takes: the record; the prompt, by its role or command; the number of each of its steps; and
    each practice of each best practice the role works by, by the best practice's kind.
    Gives: each step or practice missing, or recorded out of its place, said so that the role
    carries it out; none where the record keeps each in order.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `R-->>GD: each step, practice, or item they lack`.
    """
    raise NotImplementedError("order.lacks")

"""Decides the order that a record must keep: each step of the prompt in its order, and each
practice of each best practice within the steps, those taken while deciding before those taken
while making, in the latest pass through the steps, as a role resumed, or the orchestrator at each
turn, takes the steps again."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from record.form import Entry, Record
from record.practices import Phase, Practice


def lacks(
    record: Record, of: str, steps: Sequence[int], practices: Mapping[str, Sequence[Practice]]
) -> tuple[str, ...]:
    """What a record lacks of the steps and practices.

    Takes: the record; the prompt, by its role or command; the number of each of its steps; and
    each practice of each best practice the role works by, by the best practice's kind.
    Gives: each step or practice missing, or recorded out of its place, in the latest pass, which
    begins at the last entry of the prompt's first step, each said so that the role carries it out
    and naming the step or practice; none where that pass keeps each step in order, and each
    practice after the first step and before the last, those taken while deciding before those
    taken while making.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `R-->>GD: each step, practice, or item they lack`.
    """
    entries = list(record.entries)
    if steps:
        firsts = [n for n, e in enumerate(entries) if (e.of, e.step) == (of, steps[0])]
        entries = entries[firsts[-1] :] if firsts else []
    return _steps(entries, of, steps) + _practices(entries, of, steps, practices)


def _steps(entries: list[Entry], of: str, steps: Sequence[int]) -> tuple[str, ...]:
    """Each step of the pass missing or out of its place."""
    found, expected = [], 0
    for entry in entries:
        if entry.of != of or entry.step is None or expected >= len(steps):
            continue
        if entry.step == steps[expected]:
            expected += 1
        else:
            found.append(f"{of} step {entry.step} is recorded before step {steps[expected]}")
    after = f" after step {steps[expected - 1]}" if expected else ""
    found += [f"{of} step {n} isn't recorded{after}" for n in steps[expected:]]
    return tuple(found)


def _practices(
    entries: list[Entry], of: str, steps: Sequence[int], practices: Mapping[str, Sequence[Practice]]
) -> tuple[str, ...]:
    """Each practice of the pass missing, outside the steps, or taken while deciding after one
    taken while making."""
    at_steps = [n for n, e in enumerate(entries) if e.of == of and e.step is not None]
    first, last = (at_steps[0], at_steps[-1]) if at_steps else (-1, len(entries))
    found = []
    for kind, each in practices.items():
        places = {e.practice: n for n, e in enumerate(entries) if e.of == kind and e.practice}
        making = [places[p.id] for p in each if p.phase is Phase.MAKE and p.id in places]
        for practice in each:
            place = places.get(practice.id)
            if place is None:
                found.append(f"{kind} {practice.id} isn't recorded")
            elif steps and not first < place < last:
                found.append(f"{kind} {practice.id} is recorded outside the steps of {of}")
            elif practice.phase is Phase.DECIDE and making and place > min(making):
                found.append(f"{kind} {practice.id}, taken while deciding, comes after making")
    return tuple(found)

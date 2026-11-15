"""Decides how rn's check reads the steps of a prompt: the numbered list under `## Steps` of a
role's part in `domain/`, or of a command's `skills/<command>/SKILL.md`."""

from __future__ import annotations


def numbers(plugin_root: str, of: str) -> tuple[int, ...]:
    """The number of each step of a prompt.

    Takes: rn's folder, and the prompt, by its role, such as generator, or by its command, such as
    up.
    Gives: each step's number, in order.
    Changes: nothing.
    Refuses: fault.Wrong, where no prompt of rn's has that name; fault.CantRun, where its file
    can't be read.
    Carries: S1 `GD->>R: checks its record`, against the steps of the role's prompt.
    """
    raise NotImplementedError("steps.numbers")

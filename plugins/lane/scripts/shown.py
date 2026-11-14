"""Decides how `lay.py print` shows a Proposal to the caller: the Routes laid on the skill's step,
each Step as it'll read once laid, each Lane with its sentence and type, the commands each role may
run, the notes beside a step, and the ID, in the form that Lane's README shows."""

from __future__ import annotations

from collections.abc import Sequence

from proposal import Proposal
from steps import Role, Step


def reads(step: Step, sentences: Sequence[str]) -> str:
    """The Step as it'll read once laid: its words, then each sentence that its own words don't
    already say, each after one space."""
    raise NotImplementedError("shown.reads")


def notes(proposal: Proposal, found: Sequence[Role]) -> list[str]:
    """Each note beside the Proposal: each step that names in backticks a command its subagent may
    not run, each role whose Steps name no command, so that Lane holds only how it ends, and each
    laid sentence that the user changed, which Lane keeps as their own words."""
    raise NotImplementedError("shown.notes")


def text(proposal: Proposal, found: Sequence[Role]) -> str:
    """What `lay.py print` prints for the Proposal, ending with its ID and the line that asks for
    `yes` or what to change."""
    raise NotImplementedError("shown.text")

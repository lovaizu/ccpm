"""How Lane's sentences sit in a plugin's Steps: each sentence after the Step's own words, none
where the Step already says it word for word, so that a later Lane takes its own words out and
keeps the user's."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from form import Laid

from lay.steps import Step


@dataclass(frozen=True)
class Note:
    """A sentence that Lane laid and the user changed, kept as the user's words."""

    file: str
    step: int
    laid: str
    now: str


def strip(steps: Sequence[Step], laid: Laid) -> tuple[tuple[Step, ...], tuple[Note, ...]]:
    """Each Step without the text that the Laid names.

    Takes: the Steps as the files hold them, and the Laid.
    Gives: each Step with each sentence that it still holds word for word taken out, and a Note
    for each sentence that the user changed, which stays in the Step as theirs.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: each Step without the text that the Laid names`, S4's loop over each
    sentence that the Laid added, and `L-->>UP: each Step that remains, with the notes`.
    """
    raise NotImplementedError


def as_laid(steps: Sequence[Step], sentences: Mapping[tuple[str, int], str]) -> tuple[Step, ...]:
    """Each Step as it will read once laid.

    Takes: the Steps without the Laid's text, and each Lane's sentence by its Step's file and
    number.
    Gives: each Step with its sentences after its own words, leaving out a sentence that the Step
    already says.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    raise NotImplementedError


def lay(plugin: str, steps: Sequence[Step], version: str) -> Laid:
    """Writes each Step as laid in place of what the Laid added.

    Takes: the plugin's folder, each Step as it will read once laid, and Lane's version.
    Gives: the new Laid, with each sentence written.
    Changes: each file of the plugin that holds a Step whose text changes.
    Refuses: OSError, where a file can't be written, so that lay.py write puts back each file.
    Carries: S2 `L->>ST: writes each Lane's sentence in place of the Laid's`.
    """
    raise NotImplementedError

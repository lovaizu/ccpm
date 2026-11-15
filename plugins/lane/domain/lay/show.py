"""How lay.py print shows a Proposal, as the person reads it before they approve: the Routes of each
skill, each Lane of each role with the Step it's laid on, each Step as it will read, and the
Proposal's ID with what to reply."""

from __future__ import annotations

from collections.abc import Sequence

from form import Proposal

from lay.steps import Step


def render(proposal: Proposal, steps: Sequence[Step], proposal_id: str) -> str:
    """What lay.py print shows.

    Takes: the Proposal, each Step as it will read once laid, and the ID it's kept by.
    Gives: the words, ending with `script_calls.id_line` and the line that asks for yes or a
    change, as the README's walkthrough shows.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    raise NotImplementedError

"""Where lay.py keeps each Proposal by its ID until it's laid, `lane/<yyyymmdd>-<plugin>/` in the
system's temporary folder, and what it keeps with it: the plugin, and its Steps as print read
them."""

from __future__ import annotations

from dataclasses import dataclass

from form import Proposal

from lay.steps import Step


@dataclass(frozen=True)
class KeptProposal:
    """A Proposal as print kept it: its ID, the plugin's folder, and the Steps it was made from."""

    id: str
    plugin: str
    proposal: Proposal
    steps: tuple[Step, ...]


def keep(plugin: str, proposal: Proposal, steps: tuple[Step, ...]) -> str:
    """Keeps a Proposal that can stand.

    Takes: the plugin's folder, the Proposal, and the Steps as print read them.
    Gives: the Proposal's new ID.
    Changes: a file of the Proposal, by its ID, in the plugin's folder of Proposals.
    Refuses: OSError, where it can't be written.
    Carries: S1 `L->>P: keeps the Proposal by its ID`.
    """
    raise NotImplementedError("proposals.keep")


def find(plugin: str, proposal_id: str) -> KeptProposal | None:
    """The Proposal kept by its ID.

    Takes: the plugin's folder, and the ID.
    Gives: the KeptProposal, or None where no Proposal of the plugin has that ID.
    Changes: nothing.
    Refuses: form.OutOfForm, where the kept file isn't in its form.
    Carries: S2 `L->>P: reads the Proposal by its ID`.
    """
    raise NotImplementedError("proposals.find")

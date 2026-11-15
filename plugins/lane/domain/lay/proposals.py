"""Where lay.py keeps each Proposal by its ID until it's laid, `lane/<yyyymmdd>-<plugin>/` in the
system's temporary folder, and what it keeps with it: the plugin, and its Steps as print read
them."""

from __future__ import annotations

import dataclasses
import datetime
import glob
import json
import os
import tempfile
import uuid
from dataclasses import dataclass

from form import Proposal, proposal_text, read_proposal
from manifest import plugin_name

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
    proposal_id = uuid.uuid4().hex[:8]
    day = datetime.date.today().strftime("%Y%m%d")
    folder = os.path.join(tempfile.gettempdir(), "lane", f"{day}-{plugin_name(plugin)}")
    os.makedirs(folder, exist_ok=True)
    held = {
        "plugin": os.path.abspath(plugin),
        "proposal": json.loads(proposal_text(proposal)),
        "steps": [dataclasses.asdict(step) for step in steps],
    }
    with open(os.path.join(folder, f"{proposal_id}.json"), "w", encoding="utf-8") as f:
        json.dump(held, f)
    return proposal_id


def find(plugin: str, proposal_id: str) -> KeptProposal | None:
    """The Proposal kept by its ID.

    Takes: the plugin's folder, and the ID.
    Gives: the KeptProposal, or None where no Proposal kept for that folder has that ID; found by
    the folder, not the plugin's name, which plugin.json may no longer give as it did at print.
    Changes: nothing.
    Refuses: form.OutOfForm, where the kept file isn't in its form.
    Carries: S2 `L->>P: reads the Proposal by its ID`.
    """
    pattern = os.path.join(tempfile.gettempdir(), "lane", "*", f"{proposal_id}.json")
    found = []
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            found += [held for held in [json.load(f)] if held["plugin"] == os.path.abspath(plugin)]
    if not found:
        return None
    held = found[-1]
    steps = tuple(Step(**step) for step in held["steps"])
    proposal = read_proposal(json.dumps(held["proposal"]))
    return KeptProposal(proposal_id, held["plugin"], proposal, steps)

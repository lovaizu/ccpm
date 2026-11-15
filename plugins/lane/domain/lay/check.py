"""What a Proposal must be for lay.py to lay it in a plugin, and whose each fault is to mend: a Lane
that its type refuses, a Step it names that isn't there, or a role that a Route starts, or a skill,
with no `ends_by_result` Lane on its last Step is up's, and a plugin's file that can't carry the
Proposal is the user's, such as a Route's command that the model may call, an adapter in
hooks/adapters/ that the Proposal doesn't name, a file of Steps that two roles share, or a
subagent's file that doesn't set `background: true`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from form import Proposal
from lanes import LaneRefused, sentence

from lay.steps import Step


@dataclass(frozen=True)
class Faults:
    """The faults of a Proposal: those up mends, and those the user fixes in their plugin."""

    proposal: tuple[str, ...]
    plugin: tuple[str, ...]


@dataclass(frozen=True)
class Checked:
    """A Proposal that can stand: each Lane's sentence by its Step's file and number."""

    sentences: Mapping[tuple[str, int], str]


def check(plugin: str, proposal: Proposal, steps: Sequence[Step]) -> Checked | Faults:
    """Whether the Proposal can be laid in the plugin, with each Lane's sentence where it can.

    Takes: the plugin's folder, the Proposal, and the Steps without the Laid's text.
    Gives: Checked, with each Lane's sentence from `lanes.sentence` with its role's last Step and
    the Proposal's Routes; or Faults, where a Lane is refused, a role or skill lacks the Lane on its
    last Step, or the plugin's files can't carry the Proposal.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, `L->>ST: checks the Proposal
    against the plugin's files`, and its `alt the Proposal can't stand` and `else a file of the
    plugin can't carry it`.
    """
    last: dict[str, int] = {}
    for step in steps:
        last[step.role] = max(last.get(step.role, 0), step.number)
    sentences: dict[tuple[str, int], list[str]] = {}
    faults = []
    there = {(step.file, step.number) for step in steps}
    for lane in proposal.lanes:
        if (lane.file, lane.step) not in there:
            faults.append(f"{lane.role}'s Lane on step {lane.step}: {lane.file} holds no such Step")
            continue
        try:
            said = sentence(lane, last.get(lane.role, 0), proposal.routes)
        except LaneRefused as e:
            faults += [f"{lane.role}'s Lane on step {lane.step}: {fault}" for fault in e.faults]
            continue
        sentences.setdefault((lane.file, lane.step), []).append(said)
    if faults:
        return Faults(tuple(faults), ())
    return Checked({key: " ".join(said) for key, said in sentences.items()})

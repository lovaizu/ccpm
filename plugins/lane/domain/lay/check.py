"""What a Proposal must be for lay.py to lay it in a plugin, and whose each fault is to mend: a Lane
that its type refuses, a Step it names that isn't there, or a role that a Route starts, or a skill,
with no `ends_by_result` Lane on its last Step is up's, and a plugin's file that can't carry the
Proposal is the user's, such as a Route's command that the model may call, an adapter in
hooks/adapters/ that the Proposal doesn't name, a file of Steps that two roles share, or a
subagent's file that doesn't set `background: true`; a Lane of reads_whole or keeps_items on a role
with no Lane of keeps_steps, or of keeps_items with no adapter of a step's items, is up's too."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from form import Proposal
from lanes import LaneRefused, sentence

from lay.steps import COMMAND, Step, commands, sets


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
    the Proposal's Routes; or Faults, where a Lane is refused, the skill of a Route or a role that
    a Route starts has no Lane of `ends_by_result`, a role with a Lane of `reads_whole` or
    `keeps_items` has no Lane of `keeps_steps`, as only its Marks bound a Step, or a Lane of
    `keeps_items` lies in a Proposal that names no adapter of a step's items, each fault naming
    the role and the lane type; and where a subagent that a Route starts doesn't set
    `background: true`, a command that a Route waits for or goes after doesn't set
    `disable-model-invocation: true`, hooks/adapters/ holds a file that the Proposal's adapters
    don't name as that of a start's text, of the kept results, or of a step's items, or one file
    holds the Steps of two roles, each fault of the plugin naming the file and what to fix in it.
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
    faults += _unended(proposal)
    plugin_faults = _files(plugin, proposal, steps)
    if faults or plugin_faults:
        return Faults(tuple(faults), plugin_faults)
    return Checked({key: " ".join(said) for key, said in sentences.items()})


def _started(proposal: Proposal) -> list[str]:
    """Each role that a Route of the Proposal starts, in the order named."""
    moves = [m for route in proposal.routes for m in route.moves]
    return list(dict.fromkeys(str(m.role) for m in moves if m.kind == "start"))


def _unended(proposal: Proposal) -> list[str]:
    """A fault for each skill of a Route and each role it starts with no Lane of
    `ends_by_result`, as the guard can tell no end of theirs without it."""
    ended = {lane.role for lane in proposal.lanes if lane.type == "ends_by_result"}
    roles = dict.fromkeys([*(route.skill for route in proposal.routes), *_started(proposal)])
    return [
        f"{role} has no Lane of ends_by_result on its last Step; add one, as the guard tells its"
        " end only by the Result it gives"
        for role in roles
        if role not in ended
    ]


def _files(plugin: str, proposal: Proposal, steps: Sequence[Step]) -> tuple[str, ...]:
    """A fault for each file of the plugin that can't carry the Proposal, with what to fix."""
    faults = _foreground(plugin, proposal) + _model_called(plugin, proposal)
    return tuple(faults + _unnamed_adapters(plugin, proposal) + _shared(steps))


def _foreground(plugin: str, proposal: Proposal) -> list[str]:
    """A fault for each subagent that a Route starts whose file doesn't set `background: true`."""
    return [
        f"agents/{role}.md: set `background: true` in its front matter, as a Route starts"
        f" {role}, and the guard holds the calls only of a subagent in the background"
        for role in _started(proposal)
        if not sets(plugin, f"agents/{role}.md", "background: true")
    ]


def _model_called(plugin: str, proposal: Proposal) -> list[str]:
    """A fault for each command that a Route waits for or goes after whose SKILL.md lets the
    model call it."""
    named = [c for route in proposal.routes for c in commands(route)]
    return [
        f"skills/{command}/SKILL.md: set `disable-model-invocation: true` in its front matter,"
        f" as a Route waits for the person to type `{command}` or goes after it, which the model"
        " mustn't call"
        for command in dict.fromkeys(named)
        if not sets(plugin, f"skills/{command}/SKILL.md", COMMAND)
    ]


def _unnamed_adapters(plugin: str, proposal: Proposal) -> list[str]:
    """A fault for each file of hooks/adapters/ that the Proposal's adapters don't name; a folder
    there, such as __pycache__/, is no adapter."""
    named = {proposal.adapters.text, proposal.adapters.records}
    folder = os.path.join(plugin, "hooks", "adapters")
    listed = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    return [
        f"hooks/adapters/{name}: the Proposal names it as neither the adapter of a start's text nor"
        " that of the kept results; move it out of hooks/adapters/, which holds only those, or make"
        " it one of them as Lane's page of steps, routes, and adapters says"
        for name in listed
        if os.path.isfile(os.path.join(folder, name)) and f"hooks/adapters/{name}" not in named
    ]


def _shared(steps: Sequence[Step]) -> list[str]:
    """A fault for each file that holds the Steps of more than one role."""
    roles: dict[str, dict[str, None]] = {}
    for step in steps:
        roles.setdefault(step.file, {})[step.role] = None
    return [
        f"{file}: holds the Steps of {' and '.join(held)}; give each role a file of Steps of its"
        " own, as the guard holds each role to its own Steps"
        for file, held in roles.items()
        if len(held) > 1
    ]

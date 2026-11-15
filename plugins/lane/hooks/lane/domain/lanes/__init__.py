"""How the lane types join to judge a Lane, a start, a Call, or an end: each type found by its name
among the modules of lanes/, a Call kept where one Lane of each lane type allows it and the end's
result script kept by every type, and a start or an end kept where it keeps every Lane."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes import ends_by_result
from lanes.kind import Broken, Held, Kept, LaneType, TypeInfo, Verdict


class LaneRefused(Exception):
    """A Lane that can't stand: of no lane type, or with the faults its type finds, so that up
    mends the Proposal."""

    def __init__(self, lane: Lane, faults: Sequence[str]) -> None:
        super().__init__("\n".join(faults))
        self.lane = lane
        self.faults = tuple(faults)


def types() -> tuple[TypeInfo, ...]:
    """Each lane type, as lay.py types shows it.

    Takes: nothing.
    Gives: the TypeInfo of each module of lanes/ that gives a `TYPE`, each by the name that its
    `info` gives.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: each type`.
    """
    return tuple(each.info() for each in _types().values())


def _types() -> dict[str, LaneType]:
    """Each lane type, by its name, from each module of lanes/ that gives a `TYPE`."""
    found: dict[str, LaneType] = {}
    for module in sorted(m.name for m in pkgutil.iter_modules(__path__)):
        each = getattr(importlib.import_module(f"{__name__}.{module}"), "TYPE", None)
        if each is not None:
            found[each.info().name] = each
    return found


def sentence(lane: Lane, last_step: int, routes: Sequence[Route]) -> str:
    """The Lane's sentence, once its type finds no fault in it.

    Takes: a Lane of a Proposal, the number of its role's last Step, and the Proposal's Routes.
    Gives: the sentence that the Lane lays on its Step.
    Changes: nothing.
    Refuses: LaneRefused, where no type has the Lane's name or its type finds a fault.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
    """
    kind = _types().get(lane.type)
    if kind is None:
        raise LaneRefused(lane, [f"{lane.type} is no lane type; lay.py types gives each"])
    faults = kind.faults(lane, last_step, routes)
    if faults:
        raise LaneRefused(lane, faults)
    return kind.sentence(lane, routes)


def check_start(lanes: Sequence[Lane], asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
    """The check of a start or resume by each Lane of the role that makes it.

    Takes: the Lanes of the skill for the main conversation's start, or of the subagent's role for
    a subagent's; the start or resume; the Run and the Start that makes it; and the moves due with
    their texts.
    Gives: Kept where every Lane keeps it; else the first Broken, which for the main conversation
    is the Lane of the skill's Routes with the moves due, and for a subagent the Lane on its last
    Step with its sentence; CantCheck, with Lane's developer to fix it, where a subagent's role has
    no Lane that checks its starts.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`,
    and S6 `else it starts a role of the plugin`.
    """
    types = _types()
    for lane in lanes:
        verdict = types[lane.type].check_start(lane, asked, held, due)
        if verdict != Kept():
            return verdict
    return Kept()


def check_call(lanes: Sequence[Lane], call: Call, held: Held) -> Verdict:
    """The check of a Call by each Lane of the role.

    Takes: the role's Lanes, the Call, and what it's held to.
    Gives: Kept where a Lane of `ends_by_result` allows it, as the end's result script stands for
    every type, or else where, for each lane type that judges the Call, one of the role's Lanes of
    that type allows it; Broken with the first Lane that no other of its type outweighs, its
    sentence, and what the role may do; CantCheck where a Lane can't judge it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `G->>T: checks the Call by each Lane of the Run of up that showed that ID`, S5
    `G->>T: checks the Call by each Lane of each Run's skill`, S6 `G->>T: checks the Call by each
    Lane of the role, with the Start's run values`.
    """
    types = _types()
    judged = [(lane, types[lane.type].allows(lane, call, held)) for lane in lanes]
    if any(lane.type == "ends_by_result" and allowed for lane, allowed in judged):
        return Kept()
    for lane, allowed in judged:
        others = [a for x, a in judged if x.type == lane.type]
        if allowed is False and not any(others):
            said = types[lane.type].sentence(lane, held.routes)
            return Broken(lane, _filled(said, held), _filled(_may(lane, lanes, held), held))
    return Kept()


def _may(lane: Lane, lanes: Sequence[Lane], held: Held) -> str:
    """What the role may do in place of a Call that the Lane stops: for run_only, each command
    that a Lane of the role lets it run, the end's result script among them."""
    if lane.type != "run_only":
        return ""
    allowed = [c for x in lanes if x.type == "run_only" for c in x.args["commands"]]
    role = held.start.role if held.start else held.run.skill
    if any(x.type == "ends_by_result" for x in lanes):
        allowed += ends_by_result.commands(role, held.routes)
    named = ", ".join(f"`{c}`" for c in dict.fromkeys(allowed))
    return f"The commands you may run, each word for word: {named}."


def _filled(said: str, held: Held) -> str:
    """The words with the plugin's folder in place of `${CLAUDE_PLUGIN_ROOT}`, as a stop reaches
    the role."""
    return said.replace("${CLAUDE_PLUGIN_ROOT}", held.root)


def check_end(lanes: Sequence[Lane], end: EndAsked, held: Held) -> Verdict:
    """The check of an end by each Lane of the role.

    Takes: the role's Lanes, the end with its last message, and what it's held to.
    Gives: Kept where every Lane keeps it; else the first Broken or CantCheck, the Lane of
    `ends_by_result` checked first, so that no command of the plugin's runs for an end with no
    Result.
    Changes: whatever a command of the plugin's that a Lane runs changes.
    Refuses: nothing.
    Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each Lane
    of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
    """
    types = _types()
    ordered = sorted(lanes, key=lambda lane: lane.type != "ends_by_result")
    for lane in ordered:
        verdict = types[lane.type].check_end(lane, end, held)
        if verdict != Kept():
            return verdict
    return Kept()

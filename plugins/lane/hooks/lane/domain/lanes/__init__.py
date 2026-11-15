"""How the lane types join to judge a Lane, a start, a Call, or an end: each type found by its name
among the modules of lanes/, a Call kept where one Lane of each lane type allows it and the end's
result script kept by every type, and a start or an end kept where it keeps every Lane."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, TypeInfo, Verdict


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
    raise NotImplementedError("lanes.types")


def sentence(lane: Lane, last_step: int, routes: Sequence[Route]) -> str:
    """The Lane's sentence, once its type finds no fault in it.

    Takes: a Lane of a Proposal, the number of its role's last Step, and the Proposal's Routes.
    Gives: the sentence that the Lane lays on its Step.
    Changes: nothing.
    Refuses: LaneRefused, where no type has the Lane's name or its type finds a fault.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
    """
    raise NotImplementedError("lanes.sentence")


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
    raise NotImplementedError("lanes.check_start")


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
    raise NotImplementedError("lanes.check_call")


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
    raise NotImplementedError("lanes.check_end")
